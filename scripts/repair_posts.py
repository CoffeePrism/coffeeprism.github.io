#!/usr/bin/env python3
"""Remove invented facts from published posts, a few at a time.

Most posts were written by a model that was asked for statistics, studies and
expert quotes without being given any sources. This script finds posts that fail
the publishing checks (scripts/content_checks.py) and asks the model to delete or
rephrase only the flagged sentences. A repair is kept only if the checks then pass,
no new number appears, and at least 60% of the text remains; otherwise the post is
left untouched. Front matter, the title and the URL never change.

Usage:
    python scripts/repair_posts.py --limit 5            # repair up to 5 posts
    python scripts/repair_posts.py --limit 5 --dry-run  # report only, write nothing
    python scripts/repair_posts.py --path content/posts/<file>.md

Trial on 2026-11-19 with the free OpenRouter models: all 3 repairs were rejected by the
guards (statistics left in, or too much text removed), so nothing was written. Use a
stronger model, or revise high-traffic posts by hand (see .claude/skills/article-review).

Posts listed in data/repair_priority.txt (one file name per line, e.g. from Bing's
page report) are repaired first; the rest follow, newest first. Each run appends
what it did to data/repair_log.jsonl.
"""
import argparse
import datetime
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_checks  # noqa: E402
import generate_and_publish as gen  # noqa: E402  (providers, prompts, parser)

POSTS = Path("content/posts")
PRIORITY = Path("data/repair_priority.txt")
LOG = Path("data/repair_log.jsonl")
TAIL_MARKERS = ("<!-- related-reading-start -->", "\n---\n\n> ☕")


def split_post(text):
    """-> (front matter incl. delimiters, article body, site-added tail)."""
    end = text.index("\n---", 4) + 4
    front, rest = text[:end], text[end:]
    cut = min((rest.find(m) for m in TAIL_MARKERS if m in rest), default=len(rest))
    return front, rest[:cut], rest[cut:]


def front_value(front, key):
    m = re.search(rf'^{key}:\s*"?(.*?)"?\s*$', front, re.M)
    return m.group(1) if m else ""


def candidates():
    files = sorted(POSTS.glob("*.md"), reverse=True)
    first = []
    if PRIORITY.exists():
        names = [line.strip() for line in PRIORITY.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
        by_name = {f.name: f for f in files}
        first = [by_name[n] for n in names if n in by_name]
    seen = set(first)
    return first + [f for f in files if f not in seen]


def repair(path, dry_run=False):
    text = path.read_text(encoding="utf-8")
    front, body, tail = split_post(text)
    if re.search(r"^draft:\s*true", front, re.M):
        return None
    title = front_value(front, "title")
    problems = content_checks.findings(title, body)
    if not problems:
        return None
    record = {"file": path.name, "date": datetime.date.today().isoformat(), "problems": len(problems),
              "codes": sorted({c for c, _ in problems})}
    if dry_run:
        record["result"] = "dry-run"
        return record
    listing = "\n".join(f"- [{code}] {snippet}" for code, snippet in problems[:15])
    raw = gen.call_llm([
        {"role": "system", "content": gen.get_system_prompt()},
        {"role": "user", "content": (
            "下面这篇已发布文章里有违反事实规则的内容（没有来源的统计、研究、报告、引语、价格、网址或亲身经历）：\n"
            f"{listing}\n\n"
            "请只删除这些句子，或改写成不含这些数字、来源、引语和价格的说法；如果整段都依赖这些内容，就删掉整段。"
            "不要新增任何事实、数字、人名、机构或网址；其他段落、标题层级、列表、表格和链接原样保留。"
            "按下面的格式输出完整正文：\n"
            f"<TITLE>\n{title}\n</TITLE>\n<BODY>\n{body.strip()}\n</BODY>"
        )},
    ])
    _, _, new_body = gen.parse_structured_output(raw)
    if not raw or not new_body or new_body.strip() == raw.strip():
        record["result"] = "no-usable-reply"
        return record
    remaining = content_checks.findings(title, new_body)
    added = set(re.findall(r"\d+(?:\.\d+)?", new_body)) - set(re.findall(r"\d+(?:\.\d+)?", body))
    if remaining or added or len(new_body) < 0.6 * len(body.strip()):
        record["result"] = "rejected"
        record["why"] = (sorted({c for c, _ in remaining})[:5] or (["new numbers: " + ", ".join(sorted(added)[:5])] if added else ["too much removed"]))
        return record
    today = datetime.date.today().isoformat()
    if re.search(r"^lastmod:", front, re.M):
        front = re.sub(r"^lastmod:.*$", f"lastmod: {today}", front, count=1, flags=re.M)
    else:
        front = front.replace("\n---", f"\nlastmod: {today}\n---", 1) if front.count("\n---") == 1 else front
    path.write_text(front + "\n\n" + new_body.strip() + "\n\n" + tail.lstrip("\n"), encoding="utf-8")
    record["result"] = "repaired"
    record["chars_before"], record["chars_after"] = len(body.strip()), len(new_body.strip())
    return record


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--limit", type=int, default=5, help="maximum posts to send to the model")
    parser.add_argument("--path", help="repair this one post")
    parser.add_argument("--dry-run", action="store_true", help="report flagged posts, change nothing")
    args = parser.parse_args(argv)
    if not args.dry_run and not gen.PROVIDERS:
        print("No LLM provider configured", file=sys.stderr)
        return 2
    queue = [Path(args.path)] if args.path else candidates()
    done = []
    for path in queue:
        if len([r for r in done if r["result"] != "dry-run"]) >= args.limit or (args.dry_run and len(done) >= args.limit):
            break
        record = repair(path, dry_run=args.dry_run)
        if record:
            done.append(record)
            print(json.dumps(record, ensure_ascii=False))
    if done and not args.dry_run:
        with LOG.open("a", encoding="utf-8") as f:
            for r in done:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{sum(r['result'] == 'repaired' for r in done)} repaired, {sum(r['result'] == 'rejected' for r in done)} rejected, "
          f"{sum(r['result'] == 'no-usable-reply' for r in done)} without a usable reply.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
