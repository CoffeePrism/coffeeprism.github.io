# Coffee Prism — Stripe-verified PDF fulfillment Worker

This Cloudflare Worker serves the two PDFs (`咖啡冲煮完全指南` and `手冲咖啡大师之路`) only to verified Stripe customers, using short-lived HMAC-signed download URLs.

## Architecture

```
Stripe Payment Link
        │ paid
        ▼
coffeeprism.com/guide/thanks/?session_id=cs_xxx
        │ JS fetch
        ▼
Worker /verify  ──► Stripe API ──► (paid?)
        │ yes
        ▼
Returns { downloads: [{ url: /download?file=...&exp=...&sig=... }] }
        │ user clicks
        ▼
Worker /download  ──► HMAC + expiry check ──► R2 stream
```

- Download links are valid for **30 minutes** by default.
- Stripe `session_id` itself is not the download credential — it's only used to mint signed URLs once.

## One-time setup

You'll need: a Cloudflare account, the Wrangler CLI (`npm i -g wrangler`), and your Stripe secret key.

### 1. Authenticate Wrangler

```bash
cd worker
npm install
npx wrangler login
```

### 2. Create the R2 bucket and upload PDFs

```bash
npx wrangler r2 bucket create coffeeprism-pdfs

npx wrangler r2 object put coffeeprism-pdfs/comprehensive.pdf \
  --file="../products/咖啡冲煮完全指南-2026.pdf"

npx wrangler r2 object put coffeeprism-pdfs/pourover.pdf \
  --file="../products/手冲咖啡大师之路.pdf"
```

### 3. Set secrets

Get your Stripe secret key (rotate the leaked one first!) from
<https://dashboard.stripe.com/test/apikeys> and your Stripe Product IDs from
<https://dashboard.stripe.com/test/products>.

```bash
npx wrangler secret put STRIPE_SECRET_KEY
# paste sk_test_... when prompted

npx wrangler secret put SIGNING_SECRET
# paste output of: openssl rand -hex 32

npx wrangler secret put PRODUCT_COMPREHENSIVE
# paste prod_xxx for 《咖啡冲煮完全指南 2026》

npx wrangler secret put PRODUCT_POUROVER
# paste prod_xxx for 《手冲咖啡大师之路》
```

### 4. Deploy

```bash
npx wrangler deploy
```

After deploy, you'll see a URL like `https://coffeeprism-fulfillment.<your-subdomain>.workers.dev`.
**Copy this URL.**

### 5. Wire it into the Hugo site

Edit `hugo.toml` and add to `[params]`:

```toml
fulfillmentWorkerUrl = "https://coffeeprism-fulfillment.<your-subdomain>.workers.dev"
```

The thanks page reads this and calls `/verify` from the browser.

### 6. (Optional) Map a custom subdomain

In `wrangler.toml` uncomment the `routes` block, and in Cloudflare dashboard
add a CNAME `api` → the workers.dev URL. Then `wrangler deploy` again.

## Local dev

```bash
npx wrangler dev --local
# in another shell, test:
curl 'http://127.0.0.1:8787/verify?session_id=cs_test_xxx'
```

For local R2 testing, use `--local` flag or pre-populate via:
```bash
npx wrangler r2 object put coffeeprism-pdfs/comprehensive.pdf --file=...  --local
```

## End-to-end smoke test (after deploy)

1. Buy via Stripe Test Mode (use card `4242 4242 4242 4242`, any future date, any CVC).
2. After redirect, browser will call `/verify` and render download buttons.
3. Click download → PDF streams from R2.
4. Open the URL in another tab 31 minutes later → should return `410 Link expired`.

## Common issues

| Symptom | Cause | Fix |
|---|---|---|
| `订单状态：unpaid` | Stripe webhook still propagating | Wait 30s, refresh thanks page |
| `Stripe 鉴权失败` | Wrong `STRIPE_SECRET_KEY` | Re-run `wrangler secret put` |
| Empty `downloads` array | Product ID mismatch | Check `PRODUCT_COMPREHENSIVE` / `PRODUCT_POUROVER` match Stripe Dashboard |
| `Invalid signature` | Different `SIGNING_SECRET` between mint and verify | Make sure you didn't redeploy with a new secret mid-session |
| CORS error in browser | Origin not in allow list | Edit `ALLOWED_ORIGIN` in `src/index.js` |

## Updating PDFs

When you regenerate PDFs:

```bash
cd ../products && python3 build_pdf.py
cd ../worker
npx wrangler r2 object put coffeeprism-pdfs/comprehensive.pdf \
  --file="../products/咖啡冲煮完全指南-2026.pdf"
npx wrangler r2 object put coffeeprism-pdfs/pourover.pdf \
  --file="../products/手冲咖啡大师之路.pdf"
```

(No worker redeploy needed — R2 objects update independently.)
