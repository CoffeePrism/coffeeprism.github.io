#!/usr/bin/env python3
"""扫 content/posts/，把 title="默认标题" 的文章分类处理：
- 能从正文提取出合理标题的 → 修复 frontmatter 的 title（同步 slug + canonicalURL）
- 提取不到的 → 给 frontmatter 加 robotsNoIndex: true，不让 Google 收录

用法：
    python3 scripts/triage_broken_titles.py        # dry-run，只报告
    python3 scripts/triage_broken_titles.py --apply # 真改
"""

import re
import sys
from pathlib import Path

POSTS_DIR = Path("content/posts")
DRY_RUN = "--apply" not in sys.argv

# Markers indicating LLM output containing a title
TITLE_MARKERS = ("**标题**", "标题：", "标题:", "**标题：**", "**标题:**")


def parse_frontmatter(text):
    """Return (frontmatter_lines, body_text). Frontmatter is delimited by '---'."""
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    fm = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    return fm, body


def get_title(fm):
    for line in fm.splitlines():
        if line.startswith("title:"):
            return line.split("title:", 1)[1].strip().strip('"').strip("'")
    return ""


def has_robots_noindex(fm):
    return any("robotsNoIndex" in l for l in fm.splitlines())


def clean_title(t):
    """Strip leftover markers like 「标题：」, leading hashes, asterisks, book marks."""
    if not t:
        return t
    t = t.strip()
    # Drop common LLM prefix markers
    for marker in ("**标题**", "标题：", "标题:", "**标题：**", "**标题:**"):
        if t.startswith(marker):
            t = t[len(marker):].strip()
    # Drop leading hashes / asterisks / quotes / book marks
    t = t.lstrip("#").strip()
    t = t.strip("*").strip()
    t = t.strip("「」").strip()
    if t.startswith("《") and t.endswith("》"):
        t = t[1:-1]
    if (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
        t = t[1:-1]
    return t.strip()


def extract_title_from_body(body):
    """Try to find a real title in the body. Returns (title, line_number) or (None, None)."""
    lines = body.splitlines()

    # Pass 1: H1 markdown
    for i, line in enumerate(lines[:25]):
        s = line.strip()
        if s.startswith("# ") and not s.startswith("## "):
            t = s.lstrip("# ").strip().strip("*").strip("《》").strip()
            if 5 <= len(t) <= 80 and "默认标题" not in t:
                return t, i

    # Pass 2: 「**标题**」 marker → next non-empty line
    for i, line in enumerate(lines[:25]):
        s = line.strip()
        if any(s.startswith(m) for m in TITLE_MARKERS):
            # Title might be on same line after marker
            for marker in TITLE_MARKERS:
                if s.startswith(marker):
                    rest = s[len(marker):].strip("：: *")
                    if rest and 5 <= len(rest) <= 80:
                        return rest.strip("《》").strip(), i
            # Or on the next non-empty line
            for j in range(i + 1, min(i + 5, len(lines))):
                ns = lines[j].strip()
                if ns:
                    t = ns.lstrip("# ").strip("*").strip("《》").strip()
                    if 5 <= len(t) <= 80:
                        return t, j
            break

    # Pass 3: ## H2 that looks like a title (first big heading)
    for i, line in enumerate(lines[:25]):
        s = line.strip()
        if s.startswith("## ") and not s.startswith("### "):
            t = s.lstrip("# ").strip("*").strip("《》").strip()
            if 5 <= len(t) <= 80:
                return t, i

    # Pass 4: First substantive non-empty line if it looks like a title
    for i, line in enumerate(lines[:5]):
        s = line.strip()
        if not s:
            continue
        if s.startswith("---") or s.startswith("```"):
            continue
        # Must look title-ish: short, no period at end (Chinese 。)
        if 10 <= len(s) <= 70 and not s.endswith("。") and not s.endswith("."):
            return s.lstrip("# ").strip("*").strip("《》").strip(), i

    return None, None


def slugify_title(title):
    """Lightweight slug for canonical URL. The original filename keeps its slug;
    we just update the frontmatter slug field for SEO consistency."""
    s = title.lower()
    s = re.sub(r"[^\w一-鿿-]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:50]


def fix_frontmatter(fm, new_title=None, add_noindex=False):
    """Apply title and/or noindex update to frontmatter lines. Return new fm."""
    out = []
    title_replaced = False
    noindex_present = has_robots_noindex(fm)
    for line in fm.splitlines():
        if line.startswith("title:") and new_title:
            # Escape any " in the title
            safe = new_title.replace('"', '\\"')
            out.append(f'title: "{safe}"')
            title_replaced = True
        else:
            out.append(line)
    if add_noindex and not noindex_present:
        out.append("robotsNoIndex: true")
    return "\n".join(out)


def remove_title_marker_lines(body):
    """If body starts with the leftover title marker lines (now duplicate),
    drop them so the body doesn't repeat the title above the article."""
    lines = body.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    if not lines:
        return body
    # Drop a leading H1 / marker line if present (likely the original title)
    s = lines[0].strip()
    if (s.startswith("# ") and not s.startswith("## ")) or any(s.startswith(m) for m in TITLE_MARKERS):
        lines = lines[1:]
        # If next line was the bold-title following the marker, drop it too if it looks like a title
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines and lines[0].strip().startswith("**") and lines[0].strip().endswith("**"):
            lines = lines[1:]
    return "\n".join(lines).lstrip("\n")


def main():
    if not POSTS_DIR.exists():
        print(f"ERR: {POSTS_DIR} not found. Run from repo root.")
        sys.exit(1)

    fixed, noindexed, untouched = [], [], []
    for path in sorted(POSTS_DIR.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️  read fail {path.name}: {e}")
            continue
        fm, body = parse_frontmatter(text)
        if fm is None:
            continue
        cur_title = get_title(fm)
        if cur_title != "默认标题":
            continue  # Healthy

        new_title, _ = extract_title_from_body(body)
        if new_title:
            new_title = clean_title(new_title)
            if not new_title or len(new_title) < 5:
                new_title = None

        if new_title:
            new_fm = fix_frontmatter(fm, new_title=new_title)
            new_body = remove_title_marker_lines(body)
            new_text = "---\n" + new_fm + "\n---\n\n" + new_body
            if not DRY_RUN:
                path.write_text(new_text, encoding="utf-8")
            fixed.append((path.name, new_title))
        else:
            new_fm = fix_frontmatter(fm, add_noindex=True)
            new_text = "---\n" + new_fm + "\n---\n\n" + body
            if not DRY_RUN:
                path.write_text(new_text, encoding="utf-8")
            noindexed.append(path.name)

    print(f"\n=== {'DRY-RUN' if DRY_RUN else 'APPLIED'} ===")
    print(f"修复（提到合理标题）：{len(fixed)} 篇")
    print(f"  示例：")
    for name, title in fixed[:5]:
        print(f"    {name}  →  「{title}」")
    print(f"\n加 noindex（提不到标题）：{len(noindexed)} 篇")
    for name in noindexed[:5]:
        print(f"    {name}")
    print(f"\n（这两组之外的 {sum(1 for _ in POSTS_DIR.glob('*.md')) - len(fixed) - len(noindexed)} 篇标题正常，不动）")
    if DRY_RUN:
        print("\n👉 加 --apply 真正改文件")


if __name__ == "__main__":
    main()
