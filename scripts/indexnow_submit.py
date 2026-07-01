#!/usr/bin/env python3
"""IndexNow 批量提交：把 sitemap 里的全部 URL 推给 Bing（及所有 IndexNow 引擎）。

Bing 的索引喂 Copilot、DeepSeek 候选集和豆包全网搜索——对中英文内容都是
最高 ROI 的收录通道。IndexNow 是即时推送，比等爬虫发现快几天到几周。

用法:
  python3 scripts/indexnow_submit.py                    # 提交 sitemap 全量 URL
  python3 scripts/indexnow_submit.py URL1 URL2 ...      # 只提交指定 URL

CI 里在 deploy 成功后调用（非致命：失败只打警告）。
"""

import json
import re
import sys
import urllib.request

HOST = "www.coffeeprism.com"
KEY = "77b015f417c80918fabc459c5729ad5a"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH_LIMIT = 10000


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "coffeeprism-indexnow/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def sitemap_urls():
    """递归解析 sitemap index → 全部页面 URL。"""
    seen, out = set(), []

    def walk(sm_url):
        if sm_url in seen:
            return
        seen.add(sm_url)
        try:
            xml = fetch(sm_url)
        except Exception as e:
            print(f"⚠️  无法读取 {sm_url}: {e}")
            return
        locs = re.findall(r"<loc>([^<]+)</loc>", xml)
        for loc in locs:
            loc = loc.strip()
            if loc.endswith(".xml"):
                walk(loc)
            else:
                out.append(loc)

    walk(f"https://{HOST}/sitemap.xml")
    return out


def submit(urls):
    payload = {
        "host": HOST,
        "key": KEY,
        "keyLocation": KEY_LOCATION,
        "urlList": urls[:BATCH_LIMIT],
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f"✓ IndexNow 提交 {len(urls[:BATCH_LIMIT])} 条 URL → HTTP {r.status}")
            return True
    except urllib.error.HTTPError as e:
        # 200/202 = accepted; 4xx 打出来诊断
        print(f"⚠️  IndexNow HTTP {e.code}: {e.read().decode()[:200]}")
        return e.code in (200, 202)
    except Exception as e:
        print(f"⚠️  IndexNow 提交失败（非致命）: {e}")
        return False


if __name__ == "__main__":
    args = sys.argv[1:]
    urls = args if args else sitemap_urls()
    if not urls:
        print("⚠️  没有可提交的 URL")
        sys.exit(0)
    print(f"准备提交 {len(urls)} 条 URL（key: {KEY_LOCATION}）")
    ok = submit(urls)
    sys.exit(0 if ok else 0)  # 永远不让 CI 因此失败
