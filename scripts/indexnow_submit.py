#!/usr/bin/env python3
"""IndexNow 推送：只把最近新增/更新的 URL 推给 Bing（及所有 IndexNow 引擎）。

Bing 的索引喂 Copilot、DeepSeek 候选集和豆包全网搜索——对中英文内容都是
最高 ROI 的收录通道。IndexNow 是即时推送，比等爬虫发现快几天到几周。

IndexNow 只应该推「有变化」的 URL。以前每天把 sitemap 全量 700+ 条全推一遍
（7 月以来累计 14 万条），Bing Webmaster Tools 因此给出建议
“Avoid IndexNow Batch Mode to prevent excessive server load and potential
indexing delays”。现在默认按 sitemap 的 <lastmod> 只推最近 N 天变化的页面
（新文章、首页、所属分类页），通常每天不到 10 条。

用法:
  python3 scripts/indexnow_submit.py --diff-build public --out urls.txt
                                                     # CI：部署前把新构建的 sitemap 和线上 sitemap 比对，
                                                     # 只记下新增、lastmod 变了、或被删除/跳转的 URL
  python3 scripts/indexnow_submit.py --from-file urls.txt   # CI：部署后提交上一步记下的 URL
  python3 scripts/indexnow_submit.py                 # 最近 3 天有变化的 URL（旧做法，比对失败时兜底）
  python3 scripts/indexnow_submit.py --days 7        # 放宽窗口，比如补推漏掉的几天
  python3 scripts/indexnow_submit.py --all           # sitemap 全量（只在全站改版后手动用）
  python3 scripts/indexnow_submit.py URL1 URL2 ...   # 只提交指定 URL
  加 --dry-run 只打印、不提交

CI 里在 deploy 成功后调用（非致命：失败只打警告）。
"""

import argparse
import datetime
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HOST = "www.coffeeprism.com"
KEY = "77b015f417c80918fabc459c5729ad5a"
KEY_LOCATION = f"https://{HOST}/{KEY}.txt"
ENDPOINT = "https://api.indexnow.org/indexnow"
BATCH_LIMIT = 10000
DEFAULT_DAYS = 3  # 文章日期是北京时间、CI 跑在 UTC 且常被 GitHub 延后几小时，留余量


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "coffeeprism-indexnow/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")


def sitemap_entries():
    """递归解析 sitemap index → [(url, lastmod 或 None)]。"""
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
        if "<sitemapindex" in xml:
            for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
                walk(loc.strip())
            return
        for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
            loc = re.search(r"<loc>([^<]+)</loc>", block)
            if not loc:
                continue
            lastmod = re.search(r"<lastmod>([^<]+)</lastmod>", block)
            out.append((loc.group(1).strip(), lastmod.group(1).strip() if lastmod else None))

    walk(f"https://{HOST}/sitemap.xml")
    return out


def local_sitemap_entries(public_dir):
    """读本地构建目录里的 sitemap（含 sitemap index）→ [(url, lastmod 或 None)]。"""
    root = Path(public_dir)
    out = []

    def parse(path):
        xml = path.read_text(encoding="utf-8", errors="ignore")
        if "<sitemapindex" in xml:
            for loc in re.findall(r"<loc>([^<]+)</loc>", xml):
                rel = re.sub(r"^https?://[^/]+/", "", loc.strip())
                child = root / rel
                if child.exists():
                    parse(child)
            return
        for block in re.findall(r"<url>(.*?)</url>", xml, re.S):
            loc = re.search(r"<loc>([^<]+)</loc>", block)
            if loc:
                lastmod = re.search(r"<lastmod>([^<]+)</lastmod>", block)
                out.append((loc.group(1).strip(), lastmod.group(1).strip() if lastmod else None))

    parse(root / "sitemap.xml")
    return out


def changed_urls(new_entries, live_entries):
    """新增的、lastmod 变了的、以及从 sitemap 里消失（删除或合并跳转）的 URL。"""
    live = dict(live_entries)
    new = dict(new_entries)
    changed = [u for u, m in new_entries if u not in live or live[u] != m]
    removed = [u for u in live if u not in new]
    return changed + removed


def recent_urls(entries, days):
    """lastmod 日期（取前 10 位 YYYY-MM-DD）在最近 days 天内的 URL。"""
    cutoff = (datetime.datetime.now(datetime.timezone.utc).date()
              - datetime.timedelta(days=days)).isoformat()
    return [loc for loc, lastmod in entries if lastmod and lastmod[:10] >= cutoff]


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


def main():
    p = argparse.ArgumentParser(description="IndexNow 推送最近变化的 URL")
    p.add_argument("urls", nargs="*", help="只提交这些 URL（不读 sitemap）")
    p.add_argument("--days", type=int, default=DEFAULT_DAYS,
                   help=f"提交 lastmod 在最近 N 天内的 URL（默认 {DEFAULT_DAYS}）")
    p.add_argument("--all", action="store_true", help="提交 sitemap 全量 URL")
    p.add_argument("--dry-run", action="store_true", help="只打印，不提交")
    p.add_argument("--diff-build", metavar="DIR", help="和线上比对这个构建目录的 sitemap，把变化的 URL 写进 --out")
    p.add_argument("--out", metavar="FILE", help="--diff-build 的输出文件")
    p.add_argument("--from-file", metavar="FILE", help="提交这个文件里的 URL（每行一个）")
    args = p.parse_args()

    if args.diff_build:
        new_entries = local_sitemap_entries(args.diff_build)
        live_entries = sitemap_entries()
        if live_entries:
            urls = changed_urls(new_entries, live_entries)
            print(f"本次构建 {len(new_entries)} 条，线上 {len(live_entries)} 条，有变化 {len(urls)} 条")
        else:
            urls = recent_urls(new_entries, args.days)
            print(f"读不到线上 sitemap，改用最近 {args.days} 天的 lastmod：{len(urls)} 条")
        Path(args.out or "indexnow-urls.txt").write_text("\n".join(urls) + ("\n" if urls else ""), encoding="utf-8")
        for u in urls[:20]:
            print(f"  {u}")
        return 0

    if args.from_file:
        path = Path(args.from_file)
        urls = [u.strip() for u in path.read_text(encoding="utf-8").splitlines() if u.strip()] if path.exists() else []
    elif args.urls:
        urls = args.urls
    else:
        entries = sitemap_entries()
        urls = [loc for loc, _ in entries] if args.all else recent_urls(entries, args.days)
        scope = "全量" if args.all else f"最近 {args.days} 天有变化"
        print(f"sitemap 共 {len(entries)} 条，{scope}的 {len(urls)} 条")

    if not urls:
        print("没有需要提交的 URL")
        return 0
    for u in urls[:20]:
        print(f"  {u}")
    if len(urls) > 20:
        print(f"  …… 共 {len(urls)} 条")
    if args.dry_run:
        print("--dry-run：不提交")
        return 0
    print(f"准备提交 {len(urls)} 条 URL（key: {KEY_LOCATION}）")
    submit(urls)
    return 0  # 永远不让 CI 因此失败


if __name__ == "__main__":
    sys.exit(main())
