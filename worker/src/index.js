/**
 * Coffee Prism — Stripe-verified PDF fulfillment Worker
 *
 * Endpoints:
 *   GET /verify?session_id=cs_xxx
 *     -> verifies the Stripe Checkout session is paid, returns short-lived signed download URLs
 *
 *   GET /download?file=comprehensive|pourover&exp=<unix_ms>&sig=<hmac>
 *     -> validates HMAC + expiry, streams the PDF from R2
 *
 * Required secrets/vars (configured via wrangler):
 *   STRIPE_SECRET_KEY    — sk_test_... or sk_live_...
 *   SIGNING_SECRET       — long random string (e.g. `openssl rand -hex 32`)
 *   PRODUCT_COMPREHENSIVE — Stripe Product ID (e.g. prod_xxx) for 全面指南
 *   PRODUCT_POUROVER      — Stripe Product ID for 大师之路
 *
 * Required binding:
 *   PDFS — R2 bucket containing `comprehensive.pdf` and `pourover.pdf`
 */

const ALLOWED_ORIGIN = "https://www.coffeeprism.com";
const FALLBACK_ORIGIN = "https://coffeeprism.com";
const DOWNLOAD_TTL_MS = 30 * 60 * 1000; // 30 minutes

const FILES = {
  comprehensive: {
    name: "咖啡冲煮完全指南 2026",
    icon: "📘",
    filename: "coffee-complete-guide-2026.pdf",
    r2_key: "comprehensive.pdf",
    size: "75 页 · 25,000 字 · ~1.1 MB",
  },
  pourover: {
    name: "手冲咖啡大师之路",
    icon: "⚡",
    filename: "pourover-master-path.pdf",
    r2_key: "pourover.pdf",
    size: "58 页 · 22,000 字 · ~1.1 MB",
  },
};

function corsHeaders(request) {
  const origin = request.headers.get("Origin") || "";
  const allow =
    origin === ALLOWED_ORIGIN || origin === FALLBACK_ORIGIN
      ? origin
      : ALLOWED_ORIGIN;
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Cache-Control": "no-store",
    Vary: "Origin",
  };
}

function jsonResponse(body, status, request) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json",
      ...corsHeaders(request),
    },
  });
}

async function hmacSign(secret, payload) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    enc.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
  const sig = await crypto.subtle.sign("HMAC", key, enc.encode(payload));
  return Array.from(new Uint8Array(sig))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

async function hmacVerify(secret, payload, signatureHex) {
  const expected = await hmacSign(secret, payload);
  if (expected.length !== signatureHex.length) return false;
  let mismatch = 0;
  for (let i = 0; i < expected.length; i++) {
    mismatch |= expected.charCodeAt(i) ^ signatureHex.charCodeAt(i);
  }
  return mismatch === 0;
}

async function makeDownloadUrl(origin, fileKey, env) {
  const exp = Date.now() + DOWNLOAD_TTL_MS;
  const payload = `${fileKey}.${exp}`;
  const sig = await hmacSign(env.SIGNING_SECRET, payload);
  const u = new URL("/download", origin);
  u.searchParams.set("file", fileKey);
  u.searchParams.set("exp", String(exp));
  u.searchParams.set("sig", sig);
  return u.toString();
}

async function handleVerify(url, request, env) {
  const sessionId = url.searchParams.get("session_id");
  if (!sessionId || !sessionId.startsWith("cs_")) {
    return jsonResponse(
      { ok: false, error: "缺少有效的 session_id" },
      400,
      request
    );
  }

  // Fetch Stripe session with line items
  const stripeUrl = `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(
    sessionId
  )}?expand[]=line_items.data.price.product`;
  const stripeResp = await fetch(stripeUrl, {
    headers: { Authorization: `Bearer ${env.STRIPE_SECRET_KEY}` },
  });

  if (!stripeResp.ok) {
    const errBody = await stripeResp.text();
    console.log("Stripe error", stripeResp.status, errBody);
    return jsonResponse(
      { ok: false, error: "找不到该订单或 Stripe 鉴权失败" },
      404,
      request
    );
  }

  const session = await stripeResp.json();
  if (session.payment_status !== "paid") {
    return jsonResponse(
      {
        ok: false,
        error: `订单状态：${session.payment_status}。如已付款请等待 1 分钟后刷新。`,
      },
      402,
      request
    );
  }

  // Map Stripe products to file keys
  const productMap = {};
  if (env.PRODUCT_COMPREHENSIVE) {
    productMap[env.PRODUCT_COMPREHENSIVE] = "comprehensive";
  }
  if (env.PRODUCT_POUROVER) {
    productMap[env.PRODUCT_POUROVER] = "pourover";
  }

  const lineItems = (session.line_items && session.line_items.data) || [];
  const fileKeys = new Set();
  for (const li of lineItems) {
    const prodId = li.price && li.price.product;
    const prodIdStr =
      typeof prodId === "string"
        ? prodId
        : prodId && prodId.id
        ? prodId.id
        : null;
    const fileKey = prodIdStr ? productMap[prodIdStr] : null;
    if (fileKey) fileKeys.add(fileKey);
  }

  // Fallback: if products aren't mapped, infer from amount (defensive)
  if (fileKeys.size === 0) {
    const total = session.amount_total || 0;
    if (total <= 450) fileKeys.add("comprehensive"); // ~$3.99
    else fileKeys.add("pourover");
  }

  const origin = url.origin;
  const downloads = [];
  for (const key of fileKeys) {
    const meta = FILES[key];
    if (!meta) continue;
    downloads.push({
      key,
      name: meta.name,
      icon: meta.icon,
      filename: meta.filename,
      size: meta.size,
      url: await makeDownloadUrl(origin, key, env),
    });
  }

  return jsonResponse(
    {
      ok: true,
      session_id: sessionId,
      payment_status: session.payment_status,
      downloads,
    },
    200,
    request
  );
}

async function handleDownload(url, request, env) {
  const fileKey = url.searchParams.get("file");
  const exp = parseInt(url.searchParams.get("exp") || "0", 10);
  const sig = url.searchParams.get("sig") || "";

  if (!FILES[fileKey]) {
    return new Response("Bad file key", { status: 400 });
  }
  if (!exp || Date.now() > exp) {
    return new Response("Link expired", { status: 410 });
  }
  const ok = await hmacVerify(env.SIGNING_SECRET, `${fileKey}.${exp}`, sig);
  if (!ok) {
    return new Response("Invalid signature", { status: 403 });
  }

  const meta = FILES[fileKey];
  const obj = await env.PDFS.get(meta.r2_key);
  if (!obj) {
    return new Response("File not found in R2", { status: 404 });
  }

  return new Response(obj.body, {
    status: 200,
    headers: {
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${meta.filename}"`,
      "Cache-Control": "private, no-store",
      "X-Content-Type-Options": "nosniff",
    },
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(request) });
    }

    if (url.pathname === "/verify" && request.method === "GET") {
      return handleVerify(url, request, env);
    }

    if (url.pathname === "/download" && request.method === "GET") {
      return handleDownload(url, request, env);
    }

    if (url.pathname === "/" || url.pathname === "/health") {
      return new Response("Coffee Prism fulfillment OK", {
        headers: { "Content-Type": "text/plain" },
      });
    }

    return new Response("Not found", { status: 404 });
  },
};
