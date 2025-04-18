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

# 检查API密钥是否设置
if not OPENAI_API_KEY:
    print("错误: OPENAI_API_KEY 环境变量未设置。请设置后再运行此脚本。")
    exit(1)

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
    },
    {
        "title": "咖啡与健康",
        "subtopics": [
            "咖啡因的生理作用与适宜摄入量",
            "咖啡中的抗氧化物质研究",
            "咖啡对心脏健康的影响",
            "咖啡与运动表现的关系",
            "咖啡与认知功能的科学研究",
            "咖啡对代谢的影响",
            "低咖啡因选择及其制作方法",
            "咖啡对睡眠的影响及应对策略"
        ]
    },
    {
        "title": "咖啡品牌与故事",
        "subtopics": [
            "星巴克的全球扩张与本土化策略",
            "精品咖啡品牌的理念与实践",
            "蓝山咖啡的声誉与真相",
            "意大利经典咖啡品牌的历史",
            "北欧咖啡文化与品牌特色",
            "日本咖啡品牌的精益求精",
            "中国新兴咖啡品牌的发展",
            "咖啡创业者的成功故事"
        ]
    },
    {
        "title": "咖啡旅行",
        "subtopics": [
            "咖啡产地旅行指南",
            "世界顶级咖啡馆朝圣之旅",
            "咖啡种植园参观体验",
            "咖啡博物馆与文化中心",
            "咖啡节与展会介绍",
            "咖啡旅行中的文化体验",
            "结合咖啡的美食之旅",
            "咖啡爱好者的城市指南"
        ]
    },
    {
        "title": "可持续咖啡",
        "subtopics": [
            "公平贸易咖啡的影响与挑战",
            "有机咖啡种植的实践与益处",
            "咖啡种植的环境影响",
            "气候变化对咖啡产业的威胁",
            "咖啡副产品的创新利用",
            "可持续咖啡包装的发展",
            "消费者如何支持可持续咖啡",
            "咖啡产业的碳足迹与减排策略"
        ]
    },
    {
        "title": "咖啡与食物搭配",
        "subtopics": [
            "咖啡与巧克力的完美匹配",
            "咖啡与甜点的风味互补",
            "咖啡在烹饪中的创新应用",
            "不同咖啡与乳制品的搭配",
            "咖啡鸡尾酒的创意配方",
            "咖啡与早餐的最佳组合",
            "咖啡风味轮与食物搭配指南",
            "咖啡与异国美食的融合"
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

def generate_article_with_openai(topic_info):
    """使用OpenAI API生成咖啡相关文章"""
    main_topic = topic_info["main_topic"]
    specific_topic = topic_info["specific_topic"]
    
    print(f"正在生成关于「{main_topic}：{specific_topic}」的文章...")
    
    if not OPENAI_API_KEY:
        print("错误: 未设置OPENAI_API_KEY环境变量")
        return None
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""你是一位资深咖啡专家和作家。请创作一篇关于「{main_topic}：{specific_topic}」的中文文章，内容约1200-1500字，并提供一个有吸引力的标题。文章应面向中国咖啡爱好者，风格清新专业。

这应该是一篇高质量的niche文章，内容深入、专业且具有教育意义。请确保文章是原创的、信息丰富的，并且对咖啡爱好者有实际价值。

如果文章中涉及到具体的咖啡产品（如咖啡机、咖啡豆、咖啡杯等），请适当添加亚马逊链接，格式为[产品名称](https://www.amazon.com/dp/[ASIN]?tag=coffeeprism-20)。每篇文章可以包含2-3个相关产品推荐。

请确保添加以下内容要素:
1. 引人入胜的标题（含有主题关键词）
2. 清晰的内容结构，包括小标题和段落划分
3. 专业且实用的咖啡知识
4. 适当的个人观点和专家建议
5. 对中国咖啡爱好者的特别考虑和本地化内容

请避免以下问题:
1. 不要使用过多的营销语言
2. 不要包含虚假或未经验证的信息
3. 不要抄袭已有内容
4. 不要过多使用列表，而应该有深入的段落式讨论
"""

    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.75,
        "max_tokens": 3000
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
    lines = article_content.strip().split('\n')
    if not lines:
        return "默认标题"
        
    title = lines[0].strip()
    
    # --- 新增清理逻辑 ---
    # 移除开头的"#"、"**"、"标题："等前缀
    prefixes_to_remove = ["#", "**", "标题：", "标题:"]
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            
    # 移除结尾的"**"
    if title.endswith("**"):
        title = title[:-2].strip()
        
    # 再次移除可能因上述操作产生的多余空格或标记
    title = title.strip("* 	\n\r")
    # --- 清理逻辑结束 ---
    
    # 如果标题被引号包围，移除引号
    if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]
        
    # 如果清理后标题为空，提供默认标题
    if not title:
        return "默认标题"
        
    return title

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
    
    # 设置随机种子，确保更好的随机性
    random.seed(time.time())
    
    # 选择随机主题
    topics = select_random_coffee_topics(2)  # 生成两篇不同主题的文章
    
    # 生成并保存文章
    for i, topic in enumerate(topics, 1):
        print(f"\n=== 生成第 {i} 篇文章 ===")
        
        # 生成文章
        article_content = generate_article_with_openai(topic)
        if not article_content:
            print(f"无法生成关于「{topic['main_topic']}：{topic['specific_topic']}」的文章，跳过")
            continue
        
        # 确保所有亚马逊链接都有跟踪ID
        article_content = add_amazon_tracking_ids(article_content)
        
        # 保存文章
        success = save_article(article_content, topic)
        if success:
            print(f"第 {i} 篇文章生成并保存成功")
        else:
            print(f"第 {i} 篇文章保存失败")
    
    print("\n自动文章生成完成！")

if __name__ == "__main__":
    main() 