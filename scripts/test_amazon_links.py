#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import urllib.parse

# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")

def create_amazon_search_link(product_name):
    """
    根据产品名称创建Amazon搜索链接，并添加affiliate tag
    """
    # 对产品名称进行URL编码
    encoded_product_name = urllib.parse.quote(product_name)
    
    # 创建Amazon搜索链接
    search_url = f"https://www.amazon.com/s?k={encoded_product_name}&tag={AMAZON_ASSOCIATE_TAG}"
    return search_url

def convert_direct_to_search_link(markdown_link):
    """
    将直接产品链接转换为搜索链接
    markdown_link格式：[产品名称](https://www.amazon.com/dp/ASIN?tag=coffeeprism-20)
    """
    # 使用正则表达式提取产品名称和链接
    pattern = r'\[([^\]]+)\]\((https?://(?:www\.)?amazon\.com/dp/[A-Z0-9]{10}[^\)]*)\)'
    match = re.match(pattern, markdown_link)
    
    if not match:
        print(f"无效的Markdown链接格式: {markdown_link}")
        return markdown_link
    
    product_name = match.group(1)
    original_url = match.group(2)
    
    # 创建搜索链接
    search_url = create_amazon_search_link(product_name)
    
    # 创建新的markdown链接
    new_markdown_link = f"[{product_name}]({search_url})"
    
    return new_markdown_link

def test_link_conversion():
    """
    测试链接转换功能
    """
    # 测试用例
    test_links = [
        '[Timemore C2 MAX手动咖啡研磨器](https://www.amazon.com/dp/B0966WJ82X?tag=coffeeprism-20)',
        '[1Zpresso JX-Pro](https://www.amazon.com/dp/B08SSDL4KT?tag=coffeeprism-20)',
        '[Comandante C40 MK4](https://www.amazon.com/dp/B09MYPM4V9?tag=coffeeprism-20)'
    ]
    
    print("链接转换测试：\n")
    for link in test_links:
        print(f"原始链接: {link}")
        converted_link = convert_direct_to_search_link(link)
        print(f"转换后: {converted_link}")
        print("-" * 80)

def test_link_extraction():
    """
    测试从文章内容中提取链接
    """
    # 示例文章片段
    article_content = """
# 2024年最佳手动咖啡研磨器推荐

手动咖啡研磨器是许多咖啡爱好者的必备工具。相比电动研磨器，手动研磨器通常价格更亲民，同时在同等价位下往往能提供更好的研磨一致性。

## 推荐产品

### 1. Timemore C2 MAX

[Timemore C2 MAX手动咖啡研磨器](https://www.amazon.com/dp/B0966WJ82X?tag=coffeeprism-20)是一款性价比极高的选择。

### 2. 1Zpresso JX-Pro

[1Zpresso JX-Pro](https://www.amazon.com/dp/B08SSDL4KT?tag=coffeeprism-20)绝对是一个出色的选择。
    """
    
    print("\n文章链接提取测试：\n")
    
    # 正则表达式查找所有Amazon链接
    pattern = re.compile(r'(\[([^\]]+)\]\((https?://(?:www\.)?amazon\.com/dp/[A-Z0-9]{10}[^\)]*)\))')
    matches = list(pattern.finditer(article_content))
    
    if not matches:
        print("未在文章中找到符合模式的Amazon链接。")
        return
    
    print(f"找到 {len(matches)} 个Amazon链接:")
    for i, match in enumerate(matches, 1):
        full_link = match.group(1)
        product_name = match.group(2)
        url = match.group(3)
        print(f"{i}. 产品: {product_name}")
        print(f"   链接: {url}")
        print(f"   完整匹配: {full_link}")
        
        # 转换为搜索链接
        search_link = create_amazon_search_link(product_name)
        print(f"   转换后的搜索链接: {search_link}")
        print()

def main():
    """
    主函数
    """
    print("=" * 40)
    print("Amazon链接转换测试")
    print("=" * 40)
    
    # 显示当前配置
    print(f"Amazon Associate Tag: {AMAZON_ASSOCIATE_TAG}\n")
    
    # 测试链接转换
    test_link_conversion()
    
    # 测试从文章内容提取链接
    test_link_extraction()
    
    print("\n测试完成！")

if __name__ == "__main__":
    main() 