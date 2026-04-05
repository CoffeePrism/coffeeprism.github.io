#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量优化文章 meta description
使用 linq.ai GPT-5.4 为所有文章生成SEO优化的 meta description
"""

import os
import re
import json
import time
import sys
import concurrent.futures
from pathlib import Path
import requests

# --- Configuration ---
LINQAI_API_URL = "https://x.linq.ai/api/ai"
MODEL_NAME = "gpt-5.4"
POSTS_DIR = Path("content/posts")
BATCH_SIZE = 5          # 并发请求数
DELAY_BETWEEN = 1       # 批次间延迟(秒)
MAX_RETRIES = 3
LOG_FILE = Path("description_update_log.json")

# 需要优化的条件：过短(<80字)、过长(>160字)、模板化内容
TEMPLATE_PATTERNS = [
    "关于.*的深度探讨，为咖啡爱好者提供专业知识和实用指南",
    "深入探讨.*的专业指南",
    "探索.*的世界",
]


def call_linqai(messages, max_retries=MAX_RETRIES):
    """调用 linq.ai API"""
    for attempt in range(max_retries):
        try:
            resp = requests.post(LINQAI_API_URL, json={
                "messages": messages,
                "model": MODEL_NAME
            }, timeout=30)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(3 * (attempt + 1))
            else:
                return None
    return None


def extract_frontmatter(content):
    """提取 frontmatter 中的字段"""
    fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not fm_match:
        return None, None, None, None

    fm_text = fm_match.group(1)

    title_match = re.search(r'^title:\s*"(.+?)"', fm_text, re.MULTILINE)
    desc_match = re.search(r'^description:\s*"(.+?)"', fm_text, re.MULTILINE)
    cat_match = re.search(r'^categories:\s*\[(.+?)\]', fm_text, re.MULTILINE)

    title = title_match.group(1) if title_match else ""
    desc = desc_match.group(1) if desc_match else ""
    category = cat_match.group(1).strip('"').strip("'") if cat_match else ""

    return title, desc, category, fm_match.end()


def needs_optimization(desc):
    """判断description是否需要优化"""
    if not desc:
        return True
    if len(desc) < 80 or len(desc) > 180:
        return True
    for pattern in TEMPLATE_PATTERNS:
        if re.search(pattern, desc):
            return True
    return False


def get_article_summary(content, fm_end, max_chars=500):
    """提取文章正文摘要（去除frontmatter后的前500字）"""
    body = content[fm_end:].strip()
    # 去除markdown标记
    body = re.sub(r'^#+\s+', '', body, flags=re.MULTILINE)
    body = re.sub(r'\*\*([^*]+)\*\*', r'\1', body)
    body = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', body)
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    body = re.sub(r'---', '', body)
    body = body.strip()
    return body[:max_chars]


def generate_description(title, category, summary):
    """调用GPT-5.4生成优化的meta description"""
    prompt = f"""为以下咖啡文章生成一条SEO优化的meta description。

标题: {title}
分类: {category}
内容摘要: {summary}

要求：
- 120-155个中文字符（严格控制）
- 第一句直接回答文章核心问题（AEO优化）
- 自然包含核心关键词
- 以具体信息开头，不要用"本文将..."这类元语言
- 结尾带有轻微的行动引导（如"了解..."、"掌握..."）
- 不要用引号包裹

只输出description文本，不要有任何其他内容。"""

    result = call_linqai([
        {"role": "system", "content": "你是SEO meta description专家。只输出description文本，不加引号，不加前缀，不解释。"},
        {"role": "user", "content": prompt}
    ])

    if result:
        # 清理：去除可能的引号和前缀
        result = result.strip().strip('"').strip("'")
        result = re.sub(r'^(description|描述|meta\s*description)\s*[:：]\s*', '', result, flags=re.IGNORECASE)
        result = result.strip().strip('"').strip("'")
        # 截断到160字符
        if len(result) > 160:
            result = result[:157] + "..."
    return result


def process_single_file(filepath):
    """处理单个文件"""
    try:
        content = filepath.read_text(encoding="utf-8")
        title, old_desc, category, fm_end = extract_frontmatter(content)

        if not title:
            return {"file": filepath.name, "status": "skip", "reason": "no_frontmatter"}

        if not needs_optimization(old_desc):
            return {"file": filepath.name, "status": "skip", "reason": "already_good",
                    "desc_len": len(old_desc)}

        summary = get_article_summary(content, fm_end)
        new_desc = generate_description(title, category, summary)

        if not new_desc or len(new_desc) < 50:
            return {"file": filepath.name, "status": "fail", "reason": "bad_generation"}

        # 替换 description
        # 转义description中的双引号
        safe_desc = new_desc.replace('"', '\\"')

        if old_desc:
            old_pattern = f'description: "{old_desc}"'
            new_pattern = f'description: "{safe_desc}"'
            new_content = content.replace(old_pattern, new_pattern, 1)
        else:
            # 没有description字段，在title后添加
            new_content = content.replace(
                f'title: "{title}"',
                f'title: "{title}"\ndescription: "{safe_desc}"',
                1
            )

        filepath.write_text(new_content, encoding="utf-8")

        return {
            "file": filepath.name,
            "status": "updated",
            "old_len": len(old_desc) if old_desc else 0,
            "new_len": len(new_desc),
            "old_desc": (old_desc[:60] + "...") if old_desc and len(old_desc) > 60 else old_desc,
            "new_desc": (new_desc[:60] + "...") if len(new_desc) > 60 else new_desc,
        }

    except Exception as e:
        return {"file": filepath.name, "status": "error", "reason": str(e)}


def main():
    if not POSTS_DIR.exists():
        print("错误: content/posts 目录不存在")
        sys.exit(1)

    files = sorted(POSTS_DIR.glob("*.md"))
    print(f"共找到 {len(files)} 篇文章")

    # 先筛选出需要优化的文章
    to_process = []
    for f in files:
        content = f.read_text(encoding="utf-8")
        title, desc, _, _ = extract_frontmatter(content)
        if title and needs_optimization(desc):
            to_process.append(f)

    print(f"需要优化: {len(to_process)} 篇")
    print(f"已合格跳过: {len(files) - len(to_process)} 篇")

    if not to_process:
        print("没有需要优化的文章！")
        return

    # 批量处理
    results = []
    updated = 0
    failed = 0
    total = len(to_process)

    print(f"\n开始批量处理 (并发数: {BATCH_SIZE})...\n")

    for batch_start in range(0, total, BATCH_SIZE):
        batch = to_process[batch_start:batch_start + BATCH_SIZE]
        batch_num = batch_start // BATCH_SIZE + 1
        total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

        print(f"[批次 {batch_num}/{total_batches}] 处理 {len(batch)} 篇...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
            futures = {executor.submit(process_single_file, f): f for f in batch}
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)

                if result["status"] == "updated":
                    updated += 1
                    print(f"  ✅ {result['file'][:40]}  [{result['old_len']}→{result['new_len']}字]")
                elif result["status"] == "fail" or result["status"] == "error":
                    failed += 1
                    print(f"  ❌ {result['file'][:40]}  ({result.get('reason', '')})")

        # 批次间延迟
        if batch_start + BATCH_SIZE < total:
            time.sleep(DELAY_BETWEEN)

    # 保存日志
    log_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_files": len(files),
        "processed": total,
        "updated": updated,
        "failed": failed,
        "results": results
    }
    LOG_FILE.write_text(json.dumps(log_data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"处理完成!")
    print(f"  总文章: {len(files)}")
    print(f"  已优化: {updated}")
    print(f"  失败: {failed}")
    print(f"  跳过: {len(files) - total}")
    print(f"  日志: {LOG_FILE}")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
