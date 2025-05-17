#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import urllib.parse

# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")

# 需要处理的文件
FILES_TO_PROCESS = [
    "content/coffee-beans/ethiopian-yirgacheffe.md",
    "content/brewing-methods/pour-over-v60.md",
    "content/coffee-equipment/timemore-c2-grinder-review.md"
]

def create_amazon_search_link(product_name):
    """
    根据产品名称创建Amazon搜索链接，并添加affiliate tag
    """
    # 对产品名称进行URL编码
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
            print(f"文件 {file_path} 中未找到需要更新的链接。")
            return 0, False
        
        # 记录原始内容用于比较
        original_content = content
        updated_count = 0
        
        # 从后向前替换，避免位置变化导致的问题
        for match in reversed(matches):
            product_name = match.group(1)
            original_link = match.group(0)
            original_url = match.group(2)
            
            print(f"找到链接: {product_name} - {original_url}")
            
            # 创建新的搜索链接
            search_url = create_amazon_search_link(product_name)
            new_link = f"[{product_name}]({search_url})"
            
            # 替换链接
            content = content[:match.start()] + new_link + content[match.end():]
            updated_count += 1
            
            print(f"  已更新为: {search_url}")
        
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

def main():
    print("开始更新特定页面的Amazon链接...")
    
    # 初始化统计信息
    total_updated_links = 0
    total_modified_files = 0
    
    # 处理每个文件
    for file_path in FILES_TO_PROCESS:
        print(f"\n处理文件: {file_path}")
        updated_links, was_modified = update_amazon_links_in_file(file_path)
        
        # 更新统计信息
        if was_modified:
            total_modified_files += 1
            total_updated_links += updated_links
            print(f"文件已更新，共修改了 {updated_links} 个链接。")
        else:
            print(f"文件无需更新。")
    
    # 汇总信息
    print("\n处理完成!")
    print(f"总共处理了 {len(FILES_TO_PROCESS)} 个文件")
    print(f"修改了 {total_modified_files} 个文件")
    print(f"更新了 {total_updated_links} 个链接")

if __name__ == "__main__":
    main() 