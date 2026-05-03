#!/usr/bin/env python3
"""为每篇文章末尾注入「相关阅读」内链区块。

核心算法：
- 为每篇文章用 (tags, category, primary_keyword) 计算相似度
- 选 4 篇最相关的（tag 重叠 + category 同 + 标题关键词重叠）
- 插入到文章末尾、PDF CTA 之前（如果有 CTA 区块的话）

用法：
    python3 scripts/inject_internal_links.py        # dry-run
    python3 scripts/inject_internal_links.py --apply
    python3 scripts/inject_internal_links.py --apply --files content/posts/abc.md  # 单文件
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

POSTS_DIR = Path("content/posts")
DRY_RUN = "--apply" not in sys.argv
RELATED_HEADING = "## 相关阅读"
RELATED_MARKER_BEGIN = "<!-- related-reading-start -->"
RELATED_MARKER_END = "<!-- related-reading-end -->"
PDF_CTA_MARKERS = (
    "/guide/comprehensive/",
    "/guide/pourover/",
    "Coffee Prism 精品电子书",
    "想系统学手冲",
    "想系统学冲煮",
)
N_RELATED = 4
MIN_OVERLAP = 1  # 至少 1 个标签或同分类才算相关


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None, text, None
    end = text.find("\n---", 3)
    if end == -1:
        return None, text, None
    fm_text = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")
    return fm_text, body, end


def parse_field_list(fm, name):
    """Parse a JSON-style array or YAML list field. Returns list of strings."""
    out = []
    for line in fm.splitlines():
        line = line.rstrip()
        if line.startswith(f"{name}:"):
            rest = line.split(":", 1)[1].strip()
            if rest.startswith("[") and rest.endswith("]"):
                items = re.findall(r'"([^"]+)"', rest)
                out.extend(items)
            elif rest:
                out.append(rest.strip().strip('"').strip("'"))
            return out
    return out


def parse_field_str(fm, name):
    for line in fm.splitlines():
        if line.startswith(f"{name}:"):
            rest = line.split(":", 1)[1].strip().strip('"').strip("'")
            return rest
    return ""


def index_posts(paths):
    """Build a dict of slug -> {title, tags, category, slug, path}."""
    index = {}
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, body, _ = parse_frontmatter(text)
        if fm is None:
            continue
        title = parse_field_str(fm, "title")
        if not title or title == "默认标题":
            continue
        # Skip drafts / explicit noindex
        if "draft: true" in fm or "robotsNoIndex: true" in fm:
            continue
        slug = parse_field_str(fm, "slug") or p.stem
        tags = parse_field_list(fm, "tags")
        cats = parse_field_list(fm, "categories")
        index[slug] = {
            "title": title,
            "tags": set(t.lower() for t in tags),
            "category": (cats[0].lower() if cats else ""),
            "slug": slug,
            "path": p,
        }
    return index


def score(a, b):
    """Higher = more related."""
    if a["slug"] == b["slug"]:
        return -1
    tag_overlap = len(a["tags"] & b["tags"])
    cat_match = 1 if a["category"] and a["category"] == b["category"] else 0
    return tag_overlap * 2 + cat_match


def pick_related(post, index, n=N_RELATED):
    candidates = []
    for other in index.values():
        s = score(post, other)
        if s >= MIN_OVERLAP:
            candidates.append((s, other))
    # Sort by score desc, then by title for stable order
    candidates.sort(key=lambda x: (-x[0], x[1]["title"]))
    return [o for _, o in candidates[:n]]


def render_block(related):
    if not related:
        return ""
    lines = [RELATED_MARKER_BEGIN, "", RELATED_HEADING, ""]
    for r in related:
        lines.append(f"- [{r['title']}](/posts/{r['slug']}/)")
    lines.append("")
    lines.append(RELATED_MARKER_END)
    return "\n".join(lines)


def remove_existing_block(body):
    """Strip any existing related-reading block (so we can refresh it)."""
    pattern = re.compile(
        re.escape(RELATED_MARKER_BEGIN) + r".*?" + re.escape(RELATED_MARKER_END),
        re.DOTALL,
    )
    return pattern.sub("", body).rstrip() + "\n"


def insert_before_cta(body, block):
    """Insert block before the PDF CTA section (the `---` line that precedes CTA),
    or at the end if no CTA found."""
    if not block:
        return body
    # Find the `---` separator that introduces the CTA blockquote
    lines = body.splitlines()
    cta_start = None
    for i, line in enumerate(lines):
        if line.strip() == "---":
            # Look at next 6 lines for CTA marker
            following = "\n".join(lines[i:i + 8])
            if any(m in following for m in PDF_CTA_MARKERS):
                cta_start = i
                break

    if cta_start is None:
        # Append at end
        return body.rstrip() + "\n\n" + block + "\n"

    head = "\n".join(lines[:cta_start]).rstrip()
    tail = "\n".join(lines[cta_start:])
    return head + "\n\n" + block + "\n\n" + tail + ("\n" if not tail.endswith("\n") else "")


def process_post(path, index):
    text = path.read_text(encoding="utf-8")
    fm, body, fm_end = parse_frontmatter(text)
    if fm is None:
        return None
    slug = parse_field_str(fm, "slug") or path.stem
    if slug not in index:
        return None  # title was 默认标题 or draft

    post = index[slug]
    related = pick_related(post, index)
    if not related:
        return None

    body_clean = remove_existing_block(body)
    block = render_block(related)
    new_body = insert_before_cta(body_clean, block)

    # Normalize trailing whitespace / newlines
    new_body = new_body.rstrip() + "\n"
    new_text = "---\n" + fm + "\n---\n\n" + new_body
    if new_text == text:
        return None  # nothing changed
    return new_text


def main():
    if "--files" in sys.argv:
        idx = sys.argv.index("--files")
        targets = [Path(p) for p in sys.argv[idx + 1:]]
    else:
        targets = sorted(POSTS_DIR.glob("*.md"))

    # Build index from ALL posts (not just targets) so single-file mode still has neighbors
    full_index = index_posts(sorted(POSTS_DIR.glob("*.md")))
    print(f"索引中已知文章：{len(full_index)} 篇")

    changed = []
    skipped = 0
    for p in targets:
        try:
            new_text = process_post(p, full_index)
        except Exception as e:
            print(f"⚠️  {p.name}: {e}")
            continue
        if new_text is None:
            skipped += 1
            continue
        if not DRY_RUN:
            p.write_text(new_text, encoding="utf-8")
        changed.append(p.name)

    print(f"\n=== {'DRY-RUN' if DRY_RUN else 'APPLIED'} ===")
    print(f"注入/刷新内链：{len(changed)} 篇")
    print(f"无变化（无相关文章 / 已是最新）：{skipped} 篇")
    if changed[:5]:
        print("示例：")
        for n in changed[:5]:
            print(f"  {n}")
    if DRY_RUN:
        print("\n👉 加 --apply 真正改文件")


if __name__ == "__main__":
    main()
