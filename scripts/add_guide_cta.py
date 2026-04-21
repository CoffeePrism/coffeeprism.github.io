#!/usr/bin/env python3
"""在相关咖啡文章底部添加 PDF 指南购买 CTA"""

import re
from pathlib import Path

POSTS_DIR = Path("content/posts")

# 对应话题 → 推荐哪本书的 CTA
CTA_POUROVER = """
---

> 📘 **想系统学手冲？** [《手冲咖啡大师之路》PDF 电子书 ¥49](/guide/pourover/) — 22000 字深度内容，6 个 WBrC 冠军配方详解，萃取动力学 + 故障诊断。一次购买，终身下载。
"""

CTA_COMPREHENSIVE = """
---

> ☕ **想系统学冲煮？** [《咖啡冲煮完全指南 2026》PDF 电子书 ¥29](/guide/comprehensive/) — 75 页、10 章、从咖啡豆到拉花全覆盖，含参数速查表。一次购买，终身下载。
"""

CTA_BOTH = """
---

> ☕ **Coffee Prism 精品电子书**
> - [《咖啡冲煮完全指南 2026》¥29](/guide/comprehensive/) — 全面型，75 页，10 章
> - [《手冲咖啡大师之路》¥49](/guide/pourover/) — 专精型，58 页，冠军配方详解
"""


def has_cta(text):
    """检查是否已有 CTA"""
    return any(marker in text for marker in [
        "/guide/comprehensive/",
        "/guide/pourover/",
        "Coffee Prism 精品电子书",
    ])


def pick_cta(text):
    """根据文章话题选合适的 CTA"""
    text_lower = text.lower()
    has_pourover = any(kw in text for kw in ["手冲", "V60", "Kalita", "滤杯", "注水"])
    has_espresso = any(kw in text for kw in ["意式", "Espresso", "浓缩", "拉花", "咖啡机"])

    # 同时涉及多种方法 → 两本都推
    if has_pourover and has_espresso:
        return CTA_BOTH
    # 只说手冲 → 专精型
    if has_pourover and not has_espresso:
        return CTA_POUROVER
    # 其他都推全面型
    return CTA_COMPREHENSIVE


def process():
    updated = 0
    skipped = 0

    # 按修改时间优先处理最近/热门文章
    files = sorted(POSTS_DIR.glob("*.md"))
    matched = [f for f in files if any(
        kw in f.read_text(encoding="utf-8", errors="ignore")
        for kw in ["手冲", "意式", "萃取", "冲泡", "冲煮", "咖啡豆", "espresso"]
    )]

    print(f"找到 {len(matched)} 篇相关文章")

    # 只处理前 30 篇（避免过度添加）
    for file in matched[:30]:
        text = file.read_text(encoding="utf-8", errors="ignore")
        if has_cta(text):
            skipped += 1
            continue

        cta = pick_cta(text)
        file.write_text(text.rstrip() + "\n" + cta, encoding="utf-8")
        updated += 1

    print(f"✓ 添加 CTA: {updated} 篇")
    print(f"  已有 CTA 跳过: {skipped} 篇")
    print(f"  未处理: {len(matched) - updated - skipped} 篇（超出前30限制）")


if __name__ == "__main__":
    process()
