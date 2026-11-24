"""Delete unsourced quotes that posts attribute to named people (2026-11).

The old generator invented quotes and pinned them on people, some made up
("主理人张默分享：「……」") and some real ("蓝瓶咖啡创始人詹姆斯·弗里曼所说：「……」").
None of them has a source. This script only deletes: for each match it removes
the sentence that carries the quote (from the sentence start through the closing
quotation mark and the punctuation right after it). It never adds or rewrites
text, and it skips lines that are tables, headings or the site's own guide links.

A match needs all three: a role word or "正如", a personal name (2-3 Chinese
characters, a Latin name, or a transliterated name with "·"), and a speech verb
followed by an opening quotation mark.

Usage: python3 scripts/remove_named_quotes.py [--write] [--show N]
Without --write it only lists what it would delete.
"""
import argparse
import pathlib
import re

ROLE = (r"(?:博士|教授|咖啡师|冠军|主理人|创始人|联合创始人|烘焙师|专家|研究员|总监|经理|老板|农场主|庄园主|"
        r"大师|评审|讲师|采购|生豆商|营养师|医生|学者|作家|记者|首席[^\s，。]{0,4}|负责人|传承人|品鉴师|杯测师|咖啡农|店主)")
NAME = r"(?:[一-鿿]{1,4}·[一-鿿]{1,6}|[A-Z][A-Za-z'’-]+(?:\s[A-Z][A-Za-z'’-]+)*|[一-鿿]{2,3}(?:小姐|先生|女士)?)"
VERB = r"(?:说|表示|指出|认为|强调|分享|分享道|坦言|告诉我们|提到|透露|曾说|所说|解释|解释道|总结|感叹|笑称|回忆|说道)"
OPEN, CLOSE = "「“\"", "」”\""
MATCH = re.compile(rf"(?:{ROLE}|正如)[^。！？\n「“\"]{{0,12}}?{NAME}(?:曾经|曾)?{VERB}[：:，,]?\s*[{OPEN}]")
SKIP_LINE = re.compile(r"^\s*(?:\||#|>\s*(?:📚|📰|☕|📌))")
SENT_END = "。！？!?"


def spans(line):
    """(start, end) character spans to delete from one line."""
    out = []
    for m in MATCH.finditer(line):
        start = max(line.rfind(c, 0, m.start()) for c in SENT_END) + 1
        open_at = m.end() - 1
        close_at = -1
        for c in CLOSE:
            pos = line.find(c, open_at + 1)
            if pos != -1 and (close_at == -1 or pos < close_at):
                close_at = pos
        if close_at == -1:
            continue  # quote runs past the line: leave it for a person to fix
        end = close_at + 1
        if end < len(line) and line[end] in SENT_END + "，,":
            end += 1
        while start < len(line) and line[start] == " ":
            start += 1
        # A quote split around its attribution (“……。”某某指出，“……”): the sentence
        # start falls inside the first half, so go back to that half's opening mark.
        while start < len(line) and line[start] in CLOSE:
            opener = {"」": "「", "”": "“", "\"": "\""}[line[start]]
            back = line.rfind(opener, 0, start)
            if back == -1:
                break
            start = max(line.rfind(c, 0, back) for c in SENT_END) + 1
            while start < len(line) and line[start] == " ":
                start += 1
        out.append((start, end))
    return out


def clean(text):
    front_end = text.index("\n---", 4) + 4
    front, body = text[:front_end], text[front_end:]
    removed = []
    lines = body.split("\n")
    for i, line in enumerate(lines):
        if SKIP_LINE.match(line):
            continue
        for start, end in reversed(spans(line)):
            removed.append(line[start:end])
            line = line[:start] + line[end:]
        lines[i] = re.sub(r"^(\s*(?:[-*]|\d+\.)\s*)$", "", line) if line != lines[i] else line
    return front + "\n".join(lines), removed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=0, help="print up to N deleted sentences")
    args = ap.parse_args()
    posts, total, shown = 0, 0, 0
    for path in sorted(pathlib.Path("content/posts").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        new, removed = clean(text)
        if not removed:
            continue
        posts += 1
        total += len(removed)
        for sentence in removed:
            if shown < args.show:
                print(f"{path.name[:40]}: {sentence}")
                shown += 1
        if args.write:
            path.write_text(new, encoding="utf-8")
    print(f"{total} quotes in {posts} posts {'deleted' if args.write else 'would be deleted'}")


if __name__ == "__main__":
    main()
