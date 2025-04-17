#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import datetime
import re
import json
import time
import uuid
import random
from pathlib import Path
import slugify

# API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 咖啡主题列表
COFFEE_TOPICS = [
    {
        "title": "咖啡文化",
        "subtopics": [
            "世界各地的咖啡仪式与传统",
            "咖啡馆文化的历史与演变",
            "第三波咖啡运动的影响",
            "咖啡与艺术的交融",
            "咖啡与社交媒体的关系",
            "不同国家的咖啡饮用习惯",
            "咖啡馆作为社交和工作空间的演变"
        ]
    },
    {
        "title": "咖啡豆种类",
        "subtopics": [
            "阿拉比卡与罗布斯塔的区别与特点",
            "单一产地咖啡豆的风味特点",
            "埃塞俄比亚咖啡豆的多样性",
            "哥伦比亚咖啡豆的特色与历史",
            "肯尼亚AA咖啡豆的独特风味",
            "巴拿马翡翠庄园的瑰夏咖啡",
            "爪哇咖啡的历史与风味特征",
            "云南小粒咖啡的发展与特点",
            "稀有咖啡品种及其价值"
        ]
    },
    {
        "title": "咖啡制作技巧",
        "subtopics": [
            "手冲咖啡的进阶技巧",
            "意式浓缩的完美萃取",
            "法压壶的最佳使用方法",
            "爱乐压的创新玩法",
            "冷萃咖啡的制作与风味特点",
            "摩卡壶的传统与现代技巧",
            "虹吸壶的科学与艺术",
            "越南滴滤咖啡的独特魅力",
            "土耳其咖啡的传统冲泡方法",
            "拉花技巧与艺术表达"
        ]
    },
    {
        "title": "咖啡设备与器具",
        "subtopics": [
            "高级咖啡研磨器的对比与选择",
            "专业咖啡机的功能与维护",
            "手冲滤杯的种类与影响",
            "精准温控壶的重要性",
            "咖啡秤的应用与推荐",
            "便携咖啡设备的创新与实用性",
            "家用咖啡设备的最佳组合",
            "复古咖啡器具的现代应用",
            "高科技咖啡设备的发展趋势"
        ]
    },
    {
        "title": "咖啡烘焙",
        "subtopics": [
            "烘焙度对咖啡风味的影响",
            "家庭咖啡烘焙入门指南",
            "不同烘焙曲线的风味表现",
            "单源咖啡的最佳烘焙方式",
            "烘焙咖啡的保鲜与储存",
            "烘焙技术的历史发展",
            "直火vs热风烘焙的区别",
            "识别完美烘焙的视觉与嗅觉线索"
        ]
    }
]

def select_random_coffee_topics(count=2):
    """随机选择指定数量的咖啡主题及子主题"""
    selected_topics = []
    # 从主题列表中随机选择不重复的主题
    chosen_main_topics = random.sample(COFFEE_TOPICS, min(count, len(COFFEE_TOPICS)))
    
    for topic in chosen_main_topics:
        # 从每个主题的子主题中随机选择一个
        subtopic = random.choice(topic["subtopics"])
        selected_topics.append({
            "main_topic": topic["title"],
            "specific_topic": subtopic
        })
    
    return selected_topics

def mock_generate_article(topic_info):
    """模拟使用OpenAI API生成咖啡相关文章"""
    main_topic = topic_info["main_topic"]
    specific_topic = topic_info["specific_topic"]
    
    print(f"正在模拟生成关于「{main_topic}：{specific_topic}」的文章...")
    
    # 模拟生成的文章
    article_content = f"""# {main_topic}中的奥秘：{specific_topic}详解

在咖啡的世界里，{specific_topic}是一个充满魅力的话题。作为{main_topic}的重要组成部分，它不仅体现了咖啡文化的多样性，也展示了咖啡爱好者对品质的不懈追求。

## {specific_topic}的历史背景

{specific_topic}的起源可以追溯到几个世纪前。早在咖啡开始流行的年代，人们就已经开始关注这一领域。随着时间的推移，相关技术和理念不断发展，形成了今天我们所熟知的体系。

## 为什么{specific_topic}如此重要

对于真正的咖啡爱好者来说，了解{specific_topic}是必不可少的。它直接影响着咖啡的风味表现、质量和整体体验。无论是专业咖啡师还是家庭爱好者，掌握这方面的知识都能显著提升咖啡享受的层次。

## {specific_topic}的关键要素

在探讨{specific_topic}时，我们不能忽视以下几个关键因素：

1. 原料品质：优质的咖啡豆是基础，如[埃塞俄比亚耶加雪菲咖啡豆](https://www.amazon.com/dp/B00LKT7UZ8?tag=coffeeprism-20)提供的独特风味。

2. 工艺流程：精确的技术和适当的工具，比如使用[精准温控水壶](https://www.amazon.com/dp/B07DTMZL56?tag=coffeeprism-20)来控制水温。

3. 个人体验：每个人对咖啡的感知和偏好各不相同，因此需要不断尝试和调整。

## 实用技巧与建议

基于多年的专业经验，我向咖啡爱好者提供以下建议：

- 始终关注细节，细微的变化可能带来显著的风味差异
- 保持开放的心态，尝试不同的方法和风格
- 记录你的体验，建立个人的咖啡笔记
- 与其他咖啡爱好者交流，分享经验和见解

## 常见问题解答

在探索{specific_topic}的过程中，人们经常遇到一些疑问。以下是一些最常见问题的解答：

**问题1**：如何判断适合自己的{specific_topic}方式？
**回答**：最好的方法是通过系统性尝试，记录每次体验，逐步找到最适合自己口味的方式。

**问题2**：专业设备是否必要？
**回答**：虽然专业设备能提供更精确的控制，但入门阶段可以从基础工具开始，如[基本款手冲滤杯](https://www.amazon.com/dp/B001W6Q53C?tag=coffeeprism-20)，随着经验积累再逐步升级。

## 结语

{specific_topic}是一个不断演变的领域，充满了探索和发现的乐趣。通过持续学习和实践，每位咖啡爱好者都能在这一领域找到属于自己的乐趣和见解。

让我们共同探索咖啡世界的奥秘，享受这一古老而现代的饮品带来的无尽魅力。"""
    
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

def save_article(article_content, topic_info):
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
        
        # 创建文件名 - 添加时间戳和随机字符串确保唯一性
        today = datetime.date.today().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # 使用UUID的前8位作为唯一标识符
        slug = slugify.slugify(title, separator='-')
        filename = f"{today}-{timestamp}-{slug}-{unique_id}.md"
        filepath = content_dir / filename
        
        # 确定文章分类和标签
        category = topic_info["main_topic"]
        tags = [topic_info["specific_topic"].split("的")[0] if "的" in topic_info["specific_topic"] else topic_info["specific_topic"]]
        
        # 创建Front Matter
        front_matter = f"""---
title: "{title}"
date: {today}
draft: false
categories: ["{category}"]
tags: {json.dumps(tags, ensure_ascii=False)}
description: "关于{topic_info['specific_topic']}的深度探讨，为咖啡爱好者提供专业知识和实用指南。"
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
    print("开始自动文章生成流程（测试版）...")
    
    # 设置随机种子，确保更好的随机性
    random.seed(time.time())
    
    # 选择随机主题
    topics = select_random_coffee_topics(2)  # 生成两篇不同主题的文章
    
    # 生成并保存文章
    for i, topic in enumerate(topics, 1):
        print(f"\n=== 生成第 {i} 篇测试文章 ===")
        
        # 生成文章
        article_content = mock_generate_article(topic)
        if not article_content:
            print(f"无法生成关于「{topic['main_topic']}：{topic['specific_topic']}」的文章，跳过")
            continue
        
        # 确保所有亚马逊链接都有跟踪ID
        article_content = add_amazon_tracking_ids(article_content)
        
        # 保存文章
        success = save_article(article_content, topic)
        if success:
            print(f"第 {i} 篇测试文章生成并保存成功")
        else:
            print(f"第 {i} 篇测试文章保存失败")
    
    print("\n自动文章生成完成！")

if __name__ == "__main__":
    main() 