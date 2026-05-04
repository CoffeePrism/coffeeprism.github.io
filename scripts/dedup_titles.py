#!/usr/bin/env python3
"""扫 content/posts/ 找标题完全重复的文章，按字数 + 修改时间挑出 winner，
其他副本：
- frontmatter 加 robotsNoIndex: true（不再被 Google 收录）
- 加 canonical 字段指向 winner（告诉搜索引擎权重去 winner）
- 在文章顶部插入提示「本文已迁移至最新版本」+ 链接

Hugo 不直接支持 301，但 noindex + canonical + 顶部跳转链接的组合：
- 搜索引擎不再排名这些副本
- 已经有的入站链接的用户能跳到 winner
- canonical 把链接权重转移给 winner

用法：
    python3 scripts/dedup_titles.py        # dry-run
    python3 scripts/dedup_titles.py --apply
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

POSTS = Path("content/posts")
DRY = "--apply" not in sys.argv


def parse_fm(text):
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end == -1:
        return None, text
    return text[3:end].strip(), text[end + 4:].lstrip("\n")


def get_field(fm, name):
    for line in fm.splitlines():
        if line.startswith(f"{name}:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def get_slug(fm, p):
    s = get_field(fm, "slug")
    return s if s else p.stem


def has_field(fm, name):
    return any(line.startswith(f"{name}:") for line in fm.splitlines())


def fm_with_fields(fm, **fields):
    """Add or replace fields in frontmatter. Existing values are replaced."""
    out_lines = []
    seen = set()
    for line in fm.splitlines():
        for k in fields:
            if line.startswith(f"{k}:"):
                # Replace
                v = fields[k]
                if isinstance(v, str):
                    out_lines.append(f'{k}: "{v}"')
                else:
                    out_lines.append(f"{k}: {str(v).lower() if isinstance(v, bool) else v}")
                seen.add(k)
                break
        else:
            out_lines.append(line)
    for k, v in fields.items():
        if k in seen:
            continue
        if isinstance(v, str):
            out_lines.append(f'{k}: "{v}"')
        elif isinstance(v, bool):
            out_lines.append(f"{k}: {str(v).lower()}")
        else:
            out_lines.append(f"{k}: {v}")
    return "\n".join(out_lines)


def main():
    groups = defaultdict(list)
    for p in POSTS.glob("*.md"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        fm, body = parse_fm(text)
        if fm is None:
            continue
        title = get_field(fm, "title")
        if not title or title == "默认标题":
            continue
        groups[title].append((p, fm, body))

    dups = {t: items for t, items in groups.items() if len(items) >= 2}
    print(f"\n=== 重复标题 {len(dups)} 组 / {sum(len(v) for v in dups.values())} 篇 ===")

    consolidated = 0
    for title, items in dups.items():
        # Pick winner: longest body, then most recent mtime
        items.sort(key=lambda x: (-len(x[2]), -x[0].stat().st_mtime))
        winner_path, winner_fm, _ = items[0]
        winner_slug = get_slug(winner_fm, winner_path)
        winner_url = f"/posts/{winner_slug}/"

        print(f"\n「{title}」")
        print(f"  ⭐ winner: {winner_path.name} (slug={winner_slug})")

        for loser_path, loser_fm, loser_body in items[1:]:
            loser_slug = get_slug(loser_fm, loser_path)
            if loser_slug == winner_slug:
                # Same slug somehow, skip
                continue

            # Skip if already consolidated
            if "robotsNoIndex: true" in loser_fm and "canonicalURL" in loser_fm:
                print(f"  ↳ {loser_path.name}: 已合并过，跳过")
                continue

            new_fm = fm_with_fields(
                loser_fm,
                robotsNoIndex=True,
                canonicalURL=f"https://www.coffeeprism.com{winner_url}",
            )

            # Insert top-of-body notice
            notice = (
                f"> 📌 **本文已合并到最新版本：[{title}]({winner_url})**\n"
                f"> 旧链接保留是为了不让历史外链失效；最新最完整的内容在上面那一篇。\n\n"
            )
            if not loser_body.startswith(">"):
                new_body = notice + loser_body
            else:
                new_body = loser_body  # already has a notice

            new_text = "---\n" + new_fm + "\n---\n\n" + new_body
            print(f"  ↳ {loser_path.name}: 加 noindex + canonical + 顶部跳转")
            if not DRY:
                loser_path.write_text(new_text, encoding="utf-8")
            consolidated += 1

    print(f"\n=== {'DRY-RUN' if DRY else 'APPLIED'} ===")
    print(f"处理重复副本：{consolidated} 篇")
    print(f"保留 winner：{len(dups)} 篇")
    if DRY:
        print("\n👉 加 --apply 真正改文件")


if __name__ == "__main__":
    main()
