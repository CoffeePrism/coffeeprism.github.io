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
if not NEWSAPI_KEY:
    print("错误: NEWSAPI_KEY 环境变量未设置。请设置后再运行此脚本。")
    exit(1)

def fetch_latest_coffee_news():
    """从NewsAPI获取最新的咖啡相关新闻"""
    print("正在获取最新咖啡新闻...")
    
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
            
        print(f"成功获取 {len(articles)} 条咖啡新闻")
        for i, article in enumerate(articles, 1):
            print(f"新闻 {i}: {article['title']}")
            
        summaries = "\n\n".join([f"标题: {a['title']}\n摘要: {a['description']}\n链接: {a['url']}" for a in articles])
        return summaries
        
    except requests.exceptions.RequestException as e:
        print(f"请求NewsAPI时出错: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"错误状态码: {e.response.status_code}")
            print(f"错误响应: {e.response.text}")
        return None

def mock_generate_article_with_openai(news_summary):
    """模拟使用OpenAI API生成咖啡相关文章"""
    print("正在模拟使用OpenAI生成文章...")
    print("使用真实的新闻数据，但模拟AI生成内容（因为API限流）")
    
    # 从新闻摘要中提取标题用于文章标题
    news_items = news_summary.split("\n\n")
    titles = [item.split("\n")[0].replace("标题: ", "") for item in news_items if item.startswith("标题:")]
    main_title = titles[0] if titles else "全球咖啡趋势分析"
    
    # 模拟生成的文章
    article_content = f"""# {main_title}

咖啡，这种全球最受欢迎的饮品之一，正在经历一场前所未有的变革。根据最新的行业数据和研究成果，以下是几个值得关注的咖啡行业趋势。

## 最新咖啡行业动态

根据最新的咖啡行业新闻，我们可以观察到以下几个主要趋势：

"""

    # 根据获取的真实新闻添加内容
    for i, news_item in enumerate(news_items[:3], 1):
        lines = news_item.split("\n")
        title = lines[0].replace("标题: ", "") if len(lines) > 0 else f"趋势 {i}"
        description = lines[1].replace("摘要: ", "") if len(lines) > 1 else "详细信息暂缺"
        link = lines[2].replace("链接: ", "") if len(lines) > 2 else "#"
        
        article_content += f"### {title}\n\n{description}\n\n了解更多信息: [原文链接]({link})\n\n"
    
    # 添加一些通用的咖啡内容
    article_content += """
## 咖啡与健康

研究继续表明适量饮用咖啡与多种健康益处相关。咖啡中的抗氧化物质被认为是这些健康益处的主要来源。

特别是深度烘焙的咖啡豆中含有的某些化合物，如[埃塞俄比亚耶加雪菲咖啡豆](https://www.amazon.com/dp/B00LKT7UZ8?tag=coffeeprism-20)中特有的多酚类物质，展现出强大的抗炎和神经保护作用。

## 可持续发展成为核心关注点

气候变化正严重威胁全球咖啡产业。面对这一挑战，咖啡行业正在积极转向更可持续的种植和生产方式。

领先的咖啡品牌正在投资：
- 耐气候变化的咖啡品种研发
- 水资源保护技术
- 有机和生态友好的种植方法
- 公平贸易实践，确保种植者获得合理收入

## 创新冲泡方法的兴起

咖啡冲泡技术也在不断创新。除了传统的滴滤和浓缩咖啡外，冷萃咖啡（Cold Brew）和氮气咖啡（Nitro Coffee）继续流行，特别是在年轻消费者中。

新型家用咖啡器具，如[Fellow Stagg EKG电子温控水壶](https://www.amazon.com/dp/B07DTMZL56?tag=coffeeprism-20)和[Origami咖啡滴滤杯](https://www.amazon.com/dp/B07Z8L64TF?tag=coffeeprism-20)，正帮助咖啡爱好者在家中实现专业级的冲泡体验。

## 结语

咖啡行业正在经历一场以消费者健康意识增强、可持续发展需求和品质追求为特征的转型。作为咖啡爱好者，这是一个前所未有的激动人心的时期，我们有机会品尝到更多元、更高品质、更符合道德标准的咖啡产品。

无论您是刚开始探索咖啡世界的新手，还是资深的咖啡鉴赏家，现在都是深入了解这一迷人饮品的绝佳时机。让我们共同期待咖啡行业的更多创新。"""
    
    return article_content

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

def main():
    print("开始自动文章生成流程（混合版 - 真实新闻 + 模拟AI生成）...")
    
    # 1. 获取最新咖啡新闻（真实）
    news_summary = fetch_latest_coffee_news()
    if not news_summary:
        print("无法获取咖啡新闻，流程终止")
        return
    
    # 2. 模拟使用OpenAI生成文章
    article_content = mock_generate_article_with_openai(news_summary)
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