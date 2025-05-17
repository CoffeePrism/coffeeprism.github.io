#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import time
from pathlib import Path
from datetime import datetime

# --- Configuration ---
# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")
CONTENT_DIR = Path("content/posts")
# 用于记录处理结果的日志文件
LOG_FILE = Path("link_update_log.txt")

def create_amazon_search_link(product_name):
    """
    根据产品名称创建Amazon搜索链接，并添加affiliate tag
    """
    # 对产品名称进行URL编码
    import urllib.parse
    encoded_product_name = urllib.parse.quote(product_name)
    
    # 创建Amazon搜索链接
    search_url = f"https://www.amazon.com/s?k={encoded_product_name}&tag={AMAZON_ASSOCIATE_TAG}"
    return search_url

def update_amazon_links_in_file(file_path):
    """
    更新单个文件中的Amazon链接
    返回(更新的链接数, 文件是否被修改)
    """
    try:
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找所有Amazon直接链接
        # 格式: [产品名称](https://www.amazon.com/dp/ASIN?tag=coffeeprism-20)
        pattern = r'\[([^\]]+)\]\((https?://(?:www\.)?amazon\.com/dp/[A-Z0-9]{10}[^\)]*)\)'
        matches = list(re.finditer(pattern, content))
        
        if not matches:
            return 0, False
        
        # 记录原始内容用于比较
        original_content = content
        updated_count = 0
        
        # 从后向前替换，避免位置变化导致的问题
        for match in reversed(matches):
            product_name = match.group(1)
            original_link = match.group(0)
            
            # 创建新的搜索链接
            search_url = create_amazon_search_link(product_name)
            new_link = f"[{product_name}]({search_url})"
            
            # 替换链接
            content = content[:match.start()] + new_link + content[match.end():]
            updated_count += 1
        
        # 如果内容有变化，写回文件
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return updated_count, True
        else:
            return 0, False
            
    except Exception as e:
        print(f"处理文件 {file_path} 时出错: {e}")
        return 0, False

def process_all_articles():
    """
    处理content/posts目录下的所有文章文件
    """
    if not CONTENT_DIR.exists() or not CONTENT_DIR.is_dir():
        print(f"错误: 目录 {CONTENT_DIR} 不存在或不是目录")
        return
    
    # 初始化统计信息
    total_files = 0
    modified_files = 0
    total_links_updated = 0
    
    # 准备日志
    log_entries = [f"Amazon链接更新日志 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"]
    log_entries.append("=" * 80 + "\n\n")
    
    # 处理所有markdown文件
    for file_path in CONTENT_DIR.glob("**/*.md"):
        total_files += 1
        print(f"正在处理: {file_path}")
        
        # 更新文件中的链接
        updated_links, was_modified = update_amazon_links_in_file(file_path)
        
        # 更新统计信息
        if was_modified:
            modified_files += 1
            total_links_updated += updated_links
            log_entries.append(f"已更新 {file_path.name}: {updated_links} 个链接\n")
        else:
            log_entries.append(f"跳过 {file_path.name}: 未找到需要更新的链接\n")
        
        # 稍作延迟，避免系统负担
        time.sleep(0.1)
    
    # 汇总统计
    summary = f"\n总结:\n"
    summary += f"处理的文件总数: {total_files}\n"
    summary += f"修改的文件数量: {modified_files}\n"
    summary += f"更新的链接总数: {total_links_updated}\n"
    log_entries.append(summary)
    
    # 写入日志文件
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.writelines(log_entries)
    
    # 打印总结
    print("\n" + "=" * 40)
    print(summary)
    print(f"详细日志已保存至: {LOG_FILE}")
    print("=" * 40)

def main():
    print("开始更新Amazon链接...")
    
    # 确认继续
    print(f"即将处理 {CONTENT_DIR} 目录下的所有文章，将直接产品链接更改为搜索链接")
    confirm = input("是否继续? (y/n): ").lower()
    
    if confirm != 'y':
        print("操作已取消")
        return
    
    # 处理所有文章
    process_all_articles()
    
    print("Amazon链接更新完成!")

if __name__ == "__main__":
    main() 