#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import datetime
import re
import json
import time
from pathlib import Path
import slugify

# API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# 检查API密钥是否设置
if not OPENAI_API_KEY:
    print("错误: OPENAI_API_KEY 环境变量未设置。请设置后再运行此脚本。")
    exit(1)
    
if not NEWSAPI_KEY:
    print("错误: NEWSAPI_KEY 环境变量未设置。请设置后再运行此脚本。")
    exit(1)

def fetch_latest_coffee_news():
    """从NewsAPI获取最新的咖啡相关新闻"""
    print("正在获取最新咖啡新闻...")
    print(f"使用 NewsAPI 密钥: {NEWSAPI_KEY[:5]}...{NEWSAPI_KEY[-5:] if NEWSAPI_KEY and len(NEWSAPI_KEY) > 10 else '密钥太短'}")
    
    url = f"https://newsapi.org/v2/everything?q=coffee&sortBy=publishedAt&language=en&apiKey={NEWSAPI_KEY}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        
        if data.get('status') != 'ok':
            print(f"从NewsAPI获取数据失败: {data.get('message', '未知错误')}")
            return None
            
        articles = data.get('articles', [])[:5]  # 获取前5条最新新闻
        
        if not articles:
            print("未找到咖啡相关新闻")
            return None
            
        summaries = "\n\n".join([f"标题: {a['title']}\n摘要: {a['description']}\n链接: {a['url']}" for a in articles])
        return summaries
        
    except requests.exceptions.RequestException as e:
        print(f"请求NewsAPI时出错: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"错误状态码: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
        return None

def generate_article_with_openai(news_summary):
    """使用OpenAI API生成咖啡相关文章"""
    print("正在使用OpenAI生成文章...")
    
    if not OPENAI_API_KEY:
        print("错误: 未设置OPENAI_API_KEY环境变量")
        return None
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""你是一位资深咖啡专家和作家。请根据以下最新咖啡新闻创作一篇中文文章，内容约1000字，并提供一个有吸引力的标题。文章应面向中国咖啡爱好者，风格清新专业。

如果文章中涉及到具体的咖啡产品（如咖啡机、咖啡豆、咖啡杯等），请适当添加亚马逊链接，格式为[产品名称](https://www.amazon.com/dp/[ASIN]?tag=coffeeprism-20)。

请确保添加以下内容要素:
1. 引人入胜的标题
2. 具有可读性的段落结构和小标题
3. 实用的咖啡知识
4. 适当的个人观点

最新咖啡新闻：
{news_summary}
"""

    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        article_content = result['choices'][0]['message']['content']
        return article_content
        
    except Exception as e:
        print(f"调用OpenAI API时出错: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print(f"错误详情: {e.response.text}")
        return None

def extract_title(article_content):
    """从文章内容中提取标题"""
    # 尝试从第一行提取标题
    lines = article_content.strip().split('\n')
    title = lines[0].strip()
    
    # 如果标题以"#"开头，移除它
    if title.startswith('#'):
        title = title.lstrip('#').strip()
    
    # 如果标题被引号包围，移除引号
    if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]
    
    return title

def save_article(article_content):
    """保存生成的文章到Hugo内容目录"""
    if not article_content:
        print("错误: 没有要保存的文章内容")
        return False
    
    try:
        # 创建内容目录（如果不存在）
        content_dir = Path("content/posts")
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # 提取标题
        title = extract_title(article_content)
        
        # 创建文件名
        today = datetime.date.today().strftime("%Y-%m-%d")
        slug = slugify.slugify(title, separator='-')
        filename = f"{today}-{slug}.md"
        filepath = content_dir / filename
        
        # 创建Front Matter
        front_matter = f"""---
title: "{title}"
date: {today}
draft: false
categories: ["咖啡知识"]
tags: ["咖啡新闻", "咖啡趋势"]
---

"""
        
        # 处理文章内容 - 移除原始标题，因为我们已经在Front Matter中指定了标题
        content_lines = article_content.strip().split('\n')
        if content_lines[0].strip().startswith('#') or content_lines[0].strip() == title:
            content_lines = content_lines[1:]
        processed_content = '\n'.join(content_lines).strip()
        
        # 将文章保存到文件
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + processed_content)
        
        print(f"文章已保存至: {filepath}")
        return True
        
    except Exception as e:
        print(f"保存文章时出错: {e}")
        return False

def add_amazon_tracking_ids(article_content):
    """添加Amazon跟踪ID到文章中的亚马逊链接"""
    # 查找亚马逊链接并添加跟踪ID
    pattern = r'https?://(?:www\.)?amazon\.com/[^\s)"]+'
    
    def replace_link(match):
        url = match.group(0)
        if '?tag=' not in url and '&tag=' not in url:
            if '?' in url:
                url += '&tag=coffeeprism-20'
            else:
                url += '?tag=coffeeprism-20'
        return url
    
    return re.sub(pattern, replace_link, article_content)

def main():
    print("开始自动文章生成流程...")
    
    # 1. 获取最新咖啡新闻
    news_summary = fetch_latest_coffee_news()
    if not news_summary:
        print("无法获取咖啡新闻，流程终止")
        return
    
    # 2. 使用OpenAI生成文章
    article_content = generate_article_with_openai(news_summary)
    if not article_content:
        print("无法生成文章，流程终止")
        return
    
    # 3. 确保所有亚马逊链接都有跟踪ID
    article_content = add_amazon_tracking_ids(article_content)
    
    # 4. 保存文章
    success = save_article(article_content)
    if success:
        print("文章生成并保存成功")
    else:
        print("文章保存失败")

if __name__ == "__main__":
    main() 