"""One-off repair of Amazon affiliate links in content/ (2026-11).

Older posts linked to amazon.com searches with Chinese keywords
(https://www.amazon.com/s?k=比乐蒂摩卡壶), which return poor or no results on
amazon.com, a few links went to amazon.cn (where our US tag earns nothing) and
some had no tag at all. This script rewrites every Amazon markdown link to

    https://www.amazon.com/s?k=<English query>&tag=coffeeprism-20

using a reviewed Chinese → English mapping (TSV: original, english_query, kind,
note). Rows with kind "drop" (not something you can buy) lose the link and keep
the link text. lastmod is left alone on purpose: link maintenance is not a
content update, and touching lastmod on hundreds of posts would make the
IndexNow step submit them all at once.

Usage: python3 scripts/fix_amazon_links.py scripts/amazon_query_map.tsv [--write]
Without --write it only reports what would change.
"""
import argparse
import collections
import pathlib
import re
import sys
import urllib.parse

TAG = "coffeeprism-20"
REMOVED = "\x00"  # marks where a generic link was removed, for the tidy-up below
CJK = re.compile(r"[　-鿿＀-￯]")
LINK = re.compile(r"\[([^\]\n]*)\]\((https?://(?:www\.)?amazon\.(?:com|cn)/[^)\s]*)\)")
# Link text that names no product ("购买链接"): such links are removed outright,
# with the brackets or list item they leave behind.
GENERIC_LABELS = {"购买链接", "搜索链接", "点击查看", "书籍链接", "链接", "亚马逊链接",
                  "Amazon链接", "查看详情", "产品链接"}
# amazon.cn product links whose ASINs only exist there; keyed by link text.
CN_PRODUCTS = {
    "泰摩手冲壶": "Timemore pour over kettle",
    "费列罗咖啡秤": "coffee scale",  # Ferrero does not make coffee scales
    "咖啡风味轮": "coffee flavor wheel",
}


def load_mapping(path):
    mapping = {}
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        original, english, kind, _note = (line.split("\t") + ["", "", ""])[:4]
        if kind not in {"exact", "generic", "drop"}:
            sys.exit(f"bad kind {kind!r} for {original!r}")
        if kind != "drop" and (not english or CJK.search(english)):
            sys.exit(f"bad english query for {original!r}: {english!r}")
        mapping[original] = (english.strip(), kind)
    return mapping


def search_url(query):
    query = " ".join(query.split())
    return f"https://www.amazon.com/s?k={urllib.parse.quote_plus(query)}&tag={TAG}"


def rewrite(text, mapping, stats):
    def repl(m):
        label, url = m.group(1), m.group(2)
        parts = urllib.parse.urlsplit(url.replace("&amp;", "&"))
        params = urllib.parse.parse_qs(parts.query)
        query = (params.get("k") or params.get("field-keywords") or [""])[0].strip()
        if parts.path.startswith("/dp/") or parts.path.startswith("/gp/product/"):
            query = CN_PRODUCTS.get(label, "") if "amazon.cn" in parts.netloc else query
            if not query:
                stats["unhandled product link"] += 1
                return m.group(0)
            stats["product link → search"] += 1
        if not query:
            stats["unlinked (empty query)"] += 1
            return label
        if CJK.search(query):
            if query not in mapping:
                stats["unmapped CJK query"] += 1
                return m.group(0)
            english, kind = mapping[query]
            if kind == "drop":
                if label in GENERIC_LABELS:
                    stats["removed (generic link text)"] += 1
                    return REMOVED
                stats["unlinked (not a product)"] += 1
                return label
            stats[f"CJK → English ({kind})"] += 1
            query = english
        elif ("amazon.cn" not in parts.netloc and parts.path == "/s"
              and params.get("tag") == [TAG] and set(params) <= {"k", "tag"}):
            stats["already correct"] += 1
            return m.group(0)  # a working English search link: leave its encoding alone
        if "amazon.cn" in parts.netloc:
            stats["amazon.cn → amazon.com"] += 1
        if params.get("tag") != [TAG]:
            stats["tag added or fixed"] += 1
        return f"[{label}]({search_url(query)})"

    text = LINK.sub(repl, text)
    # Tidy only what a removed generic link left behind: "（）", "()" or an empty list item.
    text = re.sub(r"\s?[（(]\s*" + REMOVED + r"\s*[）)]", "", text)
    text = re.sub(r"(?m)^[ \t]*(?:[-*]|\d+\.)[ \t]*" + REMOVED + r"[ \t]*\n?", "", text)
    return text.replace(REMOVED, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mapping")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--content", default="content")
    args = ap.parse_args()
    mapping = load_mapping(args.mapping)
    stats, changed = collections.Counter(), 0
    for path in sorted(pathlib.Path(args.content).rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        new = rewrite(text, mapping, stats)
        if new != text:
            changed += 1
            if args.write:
                path.write_text(new, encoding="utf-8")
    for key, value in sorted(stats.items()):
        print(f"{value:6d}  {key}")
    print(f"{changed:6d}  files {'changed' if args.write else 'would change'}")


if __name__ == "__main__":
    main()
