#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
import re
import json
import time
import uuid
import random
import urllib.parse
import traceback
import xml.etree.ElementTree as ET
from pathlib import Path
import slugify
import requests

# --- Configuration ---
# linq.ai proxy API (no auth required)
LINQAI_API_URL = "https://x.linq.ai/api/ai"
MODEL_NAME = "gpt-5.4"

# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")


def call_linqai(messages, model=MODEL_NAME, max_retries=3):
    """调用 linq.ai API，支持重试"""
    for attempt in range(max_retries):
        try:
            resp = requests.post(LINQAI_API_URL, json={
                "messages": messages,
                "model": model
            }, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "")
        except Exception as e:
            print(f"  API调用失败 (尝试 {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
    return None

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

def get_system_prompt():
    """SEO/AEO/GEO 优化的系统提示词"""
    return """你是 Coffee Prism 的首席内容策略师，同时精通咖啡专业知识、搜索引擎优化（SEO）、答案引擎优化（AEO）和生成式引擎优化（GEO）。

你的核心使命：创作能被 Google、百度、ChatGPT、Perplexity、Google AI Overview 等引擎优先引用的高质量中文咖啡内容。

## 你的专业身份
- 10年以上咖啡行业经验的SCA认证咖啡师
- 深入了解中国咖啡市场（瑞幸、Manner、M Stand、Seesaw等品牌生态）
- 熟悉全球咖啡产区、处理法、烘焙与冲泡科学

## 写作原则

### E-E-A-T 信号（Google核心排名因素）
- **Experience（经验）**：融入第一人称实操经验，如"我在使用V60冲泡时发现..."
- **Expertise（专业）**：引用具体数据、研究和行业标准（SCA标准、CQI评分等）
- **Authoritativeness（权威）**：引用可验证的来源（学术论文、行业报告、权威机构）
- **Trustworthiness（可信）**：客观公正，优缺点并述，标注信息来源

### AEO/GEO 优化（面向AI引擎）
- 每个H2章节的开头用1-2句话直接回答该节的核心问题（AI引擎会优先提取这些"直答"）
- FAQ部分的每个回答都以简洁的定义句开头，再展开详细解释
- 使用清晰的因果逻辑和对比结构，便于AI理解和引用
- 在合适的位置使用编号列表、表格对比、步骤说明等结构化格式
- 包含具体的数字、比例、温度、时间等可被AI直接引用的精确数据

### 内容质量标准
- 每篇文章3000-4000字，内容必须深入透彻
- 70%段落叙述 + 30%结构化元素（列表、表格、步骤）
- 每段3-5句话，使用短句和过渡词
- 提供独创观点和实用建议，而非泛泛而谈
- 关键术语首次出现时用**加粗**标注，并给出简要解释"""


def get_article_prompt(specific_topic, main_topic):
    """生成针对特定主题的文章提示词"""
    return f"""请为 Coffee Prism 网站创作一篇关于「{specific_topic}」（所属类目：{main_topic}）的深度文章。

## 输出格式要求（严格遵循）

### 第一行：文章标题
- 以 `# ` 开头（H1 Markdown格式）
- 包含核心关键词「{specific_topic}」
- 15-35个中文字符
- 使用 "指南"、"技巧"、"深度解析"、"完全攻略" 等高点击率词
- 不要使用书名号《》

### 正文结构

**引言（200-300字）**
- 以一个引人入胜的场景、问题或数据开头
- 前100字内自然包含2次主关键词
- 明确本文的价值承诺（读者能获得什么）

**主体内容（5-7个H2章节，每个含2-3个H3）**

每个H2章节要求：
1. 标题包含长尾关键词变体
2. 开头1-2句话直接给出该节核心结论（AEO优化关键）
3. 然后展开详细论述，包含数据、案例、对比
4. 自然融入相关产品推荐（使用格式：[产品名英文](https://www.amazon.com/s?k=产品英文搜索词)）

建议的H2框架：
- {specific_topic}的基础概念与核心原理
- {specific_topic}的历史演变与发展趋势
- {specific_topic}的关键技巧与实操步骤（含精确参数）
- {specific_topic}的常见误区与专家建议
- {specific_topic}的产品/工具推荐与选购指南
- 进阶玩家的{specific_topic}高阶技巧

**常见问题解答（FAQ）** —— 这部分非常重要！
- 独立的H2章节，标题为"## 常见问题解答"
- 包含5-7个H3问题
- 问题使用自然语言长尾关键词格式，如"如何选择适合{specific_topic}的工具？"
- 每个回答80-150字：先给出直接答案，再补充细节
- 这些FAQ将被用于生成 JSON-LD FAQ Schema

**总结段落（150-200字）**
- 总结3-5个核心要点
- 给出具体的行动建议
- 以鼓励探索的语气结尾

## SEO关键词策略
- 主关键词「{specific_topic}」自然出现8-15次
- 使用LSI语义相关词（同义词、相关概念）
- 长尾关键词变体（如"如何{specific_topic}"、"{specific_topic}教程"、"{specific_topic}推荐"）
- 关键词密度1-2%，严禁堆砌

## 中国市场本地化
- 引用中国咖啡市场数据和趋势
- 提及国内知名咖啡品牌和获取渠道
- 考虑价格区间用人民币
- 提供淘宝/京东等国内平台的替代方案说明

## 禁止事项
- 不要使用"在本文中"、"总而言之"、"综上所述"等元语言
- 不要使用过度营销的话术
- 不要编造不存在的数据或研究（宁可不引也不要编）
- 不要在正文开头输出 `---`（front matter分隔符）
- 不要输出任何front matter，只输出纯Markdown文章内容

现在请创作这篇文章。"""


def generate_article(topic_info):
    """使用 linq.ai GPT-5 生成咖啡文章"""
    main_topic = topic_info["main_topic"]
    specific_topic = topic_info["specific_topic"]

    print(f"正在生成关于「{main_topic}：{specific_topic}」的文章 (模型: {MODEL_NAME})...")

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": get_article_prompt(specific_topic, main_topic)}
    ]

    article_content = call_linqai(messages)

    if not article_content:
        print("错误: API 未返回任何内容")
        return None

    # 清理可能的思考标签
    article_content = re.sub(r'<think>.*?</think>', '', article_content, flags=re.DOTALL).strip()
    # 清理开头可能误生成的 front matter
    article_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', article_content, flags=re.DOTALL).strip()

    return article_content

def generate_seo_description(title, specific_topic, article_content):
    """生成SEO优化的meta description"""
    # 尝试从文章第一段提取关键信息
    lines = article_content.strip().split('\n')
    first_paragraph = ""
    
    for line in lines:
        clean_line = line.strip()
        # 跳过标题行和空行
        if clean_line and not clean_line.startswith('#') and len(clean_line) > 50:
            first_paragraph = clean_line[:150]
            break
    
    # 如果找到了有效段落，使用它；否则生成默认描述
    if first_paragraph:
        # 确保描述在120-160字符之间（最佳SEO长度）
        description = first_paragraph[:147] + "..." if len(first_paragraph) > 147 else first_paragraph
    else:
        # 生成包含关键词的默认描述
        description = f"深入探讨{specific_topic}的专业指南。从基础概念到实战技巧，为咖啡爱好者提供全面的知识和实用建议。立即阅读了解更多！"
    
    # 确保描述长度符合SEO最佳实践（120-160字符）
    if len(description) < 120:
        description += f"详细了解{specific_topic}的各个方面。"
    
    return description[:160]  # 限制最大长度

def extract_keywords_from_content(article_content, specific_topic):
    """从文章内容中智能提取关键词作为标签"""
    # 咖啡相关的常见关键词列表
    coffee_keywords = [
        "咖啡", "咖啡豆", "手冲", "意式", "浓缩", "拉花", "烘焙", "研磨",
        "冲泡", "萃取", "风味", "酸度", "醇厚度", "咖啡机", "磨豆机",
        "V60", "法压壶", "爱乐压", "摩卡壶", "虹吸壶", "滴滤", "冷萃",
        "阿拉比卡", "罗布斯塔", "埃塞俄比亚", "哥伦比亚", "肯尼亚",
        "耶加雪菲", "瑰夏", "蓝山", "曼特宁", "精品咖啡", "单品咖啡",
        "咖啡文化", "咖啡师", "拿铁", "卡布奇诺", "美式", "咖啡馆",
        "咖啡器具", "咖啡设备", "咖啡技巧", "咖啡知识", "咖啡制作"
    ]
    
    # 从内容中查找出现的关键词
    found_keywords = []
    content_lower = article_content.lower()
    
    for keyword in coffee_keywords:
        if keyword in article_content and keyword != "咖啡":  # "咖啡"太通用了
            found_keywords.append(keyword)
    
    # 从specific_topic中提取关键部分
    topic_keywords = []
    # 处理各种分隔符
    for separator in ["的", "与", "和", "：", ":", "、", "及"]:
        if separator in specific_topic:
            parts = specific_topic.split(separator)
            topic_keywords.extend([p.strip() for p in parts if len(p.strip()) > 2])
    
    # 如果没有分隔符，直接使用topic本身
    if not topic_keywords:
        topic_keywords = [specific_topic]
    
    # 合并并去重，优先保留topic相关关键词
    all_tags = topic_keywords[:2]  # 先取主题关键词
    for kw in found_keywords:
        if kw not in all_tags and len(all_tags) < 5:  # 限制最多5个标签
            all_tags.append(kw)
    
    # 如果标签太少，添加通用标签
    if len(all_tags) < 3:
        all_tags.append("咖啡")
    
    return all_tags[:5]  # 最多返回5个标签

def extract_title(article_content):
    """从文章内容中提取标题并返回标题和需要移除的行号列表"""
    lines = article_content.strip().split('\n')
    if not lines:
        return "默认标题", []

    # --- Updated Title Extraction Logic ---
    title = "默认标题"
    title_found = False
    lines_to_remove_indices = [] # Indices of lines containing the title/marker
    
    # Scan first few lines (e.g., up to 5)
    for i, line in enumerate(lines[:5]):
        cleaned_line = line.strip()
        if not cleaned_line: # Skip empty lines
            continue

        potential_title = cleaned_line
        current_line_is_marker = False

        # Check for markers like "**标题**" on the *current* line
        title_markers = ["**标题**", "标题：", "标题:"]
        for marker in title_markers:
            if cleaned_line.startswith(marker):
                # If marker found, the *next* non-empty line should be the title
                current_line_is_marker = True
                lines_to_remove_indices.append(i)
                # Look at the next line (if it exists)
                if i + 1 < len(lines):
                    next_line_cleaned = lines[i+1].strip()
                    if next_line_cleaned:
                        potential_title = next_line_cleaned
                        lines_to_remove_indices.append(i+1)
                        title_found = True
                        break # Found title on next line
                break # Stop checking markers for this line

        if title_found: # Already found title via marker on previous line
            break
            
        if not current_line_is_marker:
            # If no marker, treat this line as potential title
            # Basic check: not too long, doesn't look like paragraph start
            if len(cleaned_line) < 100 and cleaned_line == potential_title: # Ensure it hasn't been overwritten by marker logic
                lines_to_remove_indices = [i] # Reset indices if we are taking this line
                title_found = True
                # No break here, continue scanning in case a better marker appears later?
                # Let's break for simplicity: assume first plausible line is title if no marker found
                break 

    # If no title found in scan, fallback to first non-empty line
    if not title_found:
        for i, line in enumerate(lines):
            cleaned_line = line.strip()
            if cleaned_line:
                potential_title = cleaned_line
                lines_to_remove_indices = [i]
                title_found = True
                break
        if not title_found: # Still no title found (e.g., empty content)
             return "默认标题", []
    
    # --- Clean up the extracted title ---
    title = potential_title
    # Remove prefixes like "#", "**"
    prefixes_to_remove = ["#", "**"]
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            
    # Remove trailing "**"
    if title.endswith("**"):
        title = title[:-2].strip()
        
    # Remove surrounding quotes (", ')
    if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]
        
    # ---> NEW: Remove surrounding book title marks 《》
    if title.startswith('《') and title.endswith('》'):
        title = title[1:-1]
        
    # Strip extra whitespace or markers again
    title = title.strip("* \t\n\r")
    # --- Clean up logic ends ---
    
    # ---> NEW: Handle specific "---" title case <---
    if title == "---":
        print("警告：检测到无效标题 '---'，将尝试在正文中查找标题。")
        title = "默认标题" # Reset to default
        title_found = False # Reset found flag
        lines_to_remove_indices = [] # Reset indices
        # Re-scan lines specifically looking for marker or H1
        for i, line in enumerate(lines[:10]): # Scan a bit further
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
            
            # Check for marker first
            title_markers = ["**标题**", "标题：", "标题:"]
            for marker in title_markers:
                 if cleaned_line.startswith(marker):
                    lines_to_remove_indices.append(i)
                    if i + 1 < len(lines):
                        next_line_cleaned = lines[i+1].strip()
                        if next_line_cleaned:
                            title = next_line_cleaned # Found the real title
                            lines_to_remove_indices.append(i+1)
                            title_found = True
                            break
                    break # Stop checking markers
            if title_found: break
            
            # Check for H1 markdown
            if cleaned_line.startswith('# '):
                 title = cleaned_line[2:].strip()
                 lines_to_remove_indices = [i]
                 title_found = True
                 break
                 
        if title_found:
             # Re-apply cleaning to the newly found title
             if title.startswith('《') and title.endswith('》'): title = title[1:-1]
             title = title.strip("* \t\n\r")
        else:
             print("警告：无法在 '---' 标题后找到替代标题，将使用默认标题。")
             title = "默认标题"
             lines_to_remove_indices = [] # Cannot remove anything if we didn't find it

    # Provide default title if empty after cleaning
    if not title:
        return "默认标题", [] # Return empty list if we can't find a valid title
        
    # Return the cleaned title and the indices of the lines it came from
    return title, lines_to_remove_indices

def extract_faq_from_content(article_content):
    """从文章中提取FAQ问答对，用于生成JSON-LD FAQ Schema"""
    faq_items = []
    lines = article_content.split('\n')
    in_faq_section = False
    current_question = None
    current_answer_lines = []

    for line in lines:
        stripped = line.strip()
        # 检测FAQ章节开始
        if re.match(r'^##\s+.*(常见问题|FAQ|问答|Q\s*&\s*A)', stripped, re.IGNORECASE):
            in_faq_section = True
            continue
        # 如果在FAQ章节中遇到新的H2，结束FAQ
        if in_faq_section and re.match(r'^##\s+', stripped) and not re.match(r'^###', stripped):
            if current_question and current_answer_lines:
                answer = ' '.join(current_answer_lines).strip()
                if answer:
                    faq_items.append({"q": current_question, "a": answer})
            break
        # 在FAQ章节中，H3是问题
        if in_faq_section and re.match(r'^###\s+', stripped):
            # 保存之前的问答
            if current_question and current_answer_lines:
                answer = ' '.join(current_answer_lines).strip()
                if answer:
                    faq_items.append({"q": current_question, "a": answer})
            current_question = re.sub(r'^###\s+', '', stripped).strip()
            current_answer_lines = []
        elif in_faq_section and current_question and stripped:
            # 跳过分隔线
            if stripped == '---':
                continue
            current_answer_lines.append(stripped)

    # 保存最后一个问答
    if current_question and current_answer_lines:
        answer = ' '.join(current_answer_lines).strip()
        if answer:
            faq_items.append({"q": current_question, "a": answer})

    return faq_items[:7]  # 最多7个FAQ


def save_article(article_content, topic_info):
    """保存生成的文章到Hugo内容目录"""
    if not article_content:
        print("错误: 没有要保存的文章内容")
        return False
    
    try:
        # Create content directory if it doesn't exist
        content_dir = Path("content/posts")
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # --- UPDATED: Extract title and lines to remove ---
        title, title_line_indices = extract_title(article_content)
        if not title_line_indices and title == "默认标题":
             print("警告：无法从内容中提取有效标题，将使用默认标题。")
        elif not title_line_indices:
             print(f"警告：提取到标题 \"{title}\" 但无法确定原始行号，可能无法从正文中正确移除标题行。")
        
        # Create filename - add timestamp and unique ID
        today = datetime.date.today().strftime("%Y-%m-%d")
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        unique_id = str(uuid.uuid4())[:8] # Use first 8 chars of UUID
        # Slugify handles potential unsafe characters in title for filename
        slug = slugify.slugify(title, separator='-', max_length=50) # Limit slug length
        if not slug: # Handle cases where title results in empty slug
             slug = "article"
        filename = f"{today}-{timestamp}-{slug}-{unique_id}.md"
        filepath = content_dir / filename
        
        # Determine category and tags using improved extraction
        category = topic_info["main_topic"]
        
        # Use the new intelligent keyword extraction for tags
        tags = extract_keywords_from_content(article_content, topic_info["specific_topic"])
        
        # Generate SEO-optimized meta description
        seo_description = generate_seo_description(title, topic_info["specific_topic"], article_content)
        
        # 从文章中提取FAQ用于结构化数据
        faq_items = extract_faq_from_content(article_content)

        # Create Front Matter with SEO optimization
        faq_json = json.dumps(faq_items, ensure_ascii=False) if faq_items else "[]"
        front_matter = f"""---
title: "{title}"
date: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
lastmod: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
draft: false
categories: ["{category}"]
tags: {json.dumps(tags, ensure_ascii=False)}
description: "{seo_description}"
keywords: {json.dumps(tags[:5], ensure_ascii=False)}
author: "Coffee Prism"
faq: {faq_json}
slug: "{slug}"
canonicalURL: "https://www.coffeeprism.com/posts/{slug}/"
---

"""
        
        # --- UPDATED: Process article content - remove original title line(s) based on index ---
        content_lines = article_content.strip().split('\n')
        # Create the processed content by excluding the title lines
        processed_content_lines = []
        for i, line in enumerate(content_lines):
            if i not in title_line_indices:
                processed_content_lines.append(line)
        
        processed_content = '\n'.join(processed_content_lines).strip()
        # Add a check: If the first line of processed content STILL looks like the title, remove it (fallback)
        if processed_content_lines:
             first_processed_line_clean = processed_content_lines[0].strip().lstrip('#').strip("* \t\n\r")
             # Also check variations like quotes or book marks if they weren't cleaned perfectly by extract_title
             if first_processed_line_clean == title or \
                (first_processed_line_clean.startswith('《') and first_processed_line_clean.endswith('》') and first_processed_line_clean[1:-1] == title) or \
                (first_processed_line_clean.startswith('"') and first_processed_line_clean.endswith('"') and first_processed_line_clean[1:-1] == title):
                  print(f"警告：检测到可能的重复标题行（\"{processed_content_lines[0]}\"），将额外移除。")
                  processed_content = '\n'.join(processed_content_lines[1:]).strip()

        # Save the article
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + processed_content)
        
        print(f"文章已保存至: {filepath}")
        return True
        
    except Exception as e:
        print(f"保存文章时出错: {e}")
        # import traceback
        # print(traceback.format_exc()) # Uncomment for detailed stack trace
        return False

def check_content_quality(article_content, title, specific_topic):
    """检查文章内容质量，提供SEO和可读性反馈"""
    print("\n=== 内容质量检查 ===")
    
    issues = []
    warnings = []
    
    # 1. 检查文章长度
    word_count = len(article_content)
    char_count = len(article_content.replace(' ', '').replace('\n', ''))
    print(f"📊 文章长度: {char_count} 字符")
    
    if char_count < 2000:
        issues.append(f"⚠️  文章过短 ({char_count}字)，建议至少2500字以上")
    elif char_count < 2500:
        warnings.append(f"⚡ 文章略短 ({char_count}字)，建议增加到2500-3500字")
    else:
        print(f"✅ 文章长度良好 ({char_count}字)")
    
    # 2. 检查标题中的关键词
    if specific_topic in title:
        print(f"✅ 标题包含主关键词「{specific_topic}」")
    else:
        issues.append(f"⚠️  标题未包含主关键词「{specific_topic}」")
    
    # 3. 检查关键词密度
    keyword_count = article_content.count(specific_topic)
    keyword_density = (keyword_count * len(specific_topic) / char_count) * 100 if char_count > 0 else 0
    print(f"📈 关键词「{specific_topic}」出现 {keyword_count} 次，密度: {keyword_density:.2f}%")
    
    if keyword_count < 5:
        issues.append(f"⚠️  关键词出现次数过少 ({keyword_count}次)，建议8-12次")
    elif keyword_count > 20:
        warnings.append(f"⚡ 关键词可能过多 ({keyword_count}次)，注意避免堆砌")
    else:
        print(f"✅ 关键词频率合理")
    
    # 4. 检查标题结构 (H2, H3)
    h2_count = article_content.count('\n## ')
    h3_count = article_content.count('\n### ')
    print(f"📋 标题结构: {h2_count} 个H2标题, {h3_count} 个H3标题")
    
    if h2_count < 4:
        issues.append(f"⚠️  H2标题过少 ({h2_count}个)，建议至少5-7个主要章节")
    else:
        print(f"✅ 标题结构良好")
    
    # 5. 检查是否包含FAQ
    has_faq = any(keyword in article_content for keyword in ["常见问题", "FAQ", "问答", "Q&A", "疑问解答"])
    if has_faq:
        print("✅ 包含FAQ部分")
    else:
        warnings.append("⚡ 建议添加FAQ部分以提升SEO")
    
    # 6. 检查段落数量
    paragraphs = [p for p in article_content.split('\n\n') if len(p.strip()) > 50]
    print(f"📝 有效段落数: {len(paragraphs)}")
    
    if len(paragraphs) < 10:
        warnings.append(f"⚡ 段落较少 ({len(paragraphs)}个)，建议增加内容深度")
    
    # 7. 检查产品链接
    amazon_links = article_content.count('amazon.com')
    print(f"🔗 Amazon产品链接: {amazon_links} 个")
    
    if amazon_links == 0:
        warnings.append("⚡ 未发现Amazon产品链接，可适当添加2-4个相关产品推荐")
    elif amazon_links > 5:
        warnings.append(f"⚡ Amazon链接较多 ({amazon_links}个)，避免过度商业化")
    
    # 输出结果
    if issues:
        print("\n❌ 发现以下问题:")
        for issue in issues:
            print(f"  {issue}")
    
    if warnings:
        print("\n⚠️  优化建议:")
        for warning in warnings:
            print(f"  {warning}")
    
    if not issues and not warnings:
        print("\n🎉 内容质量优秀！符合SEO最佳实践。")
    
    print("=" * 50)
    
    return len(issues) == 0  # 返回True如果没有严重问题

def add_amazon_tracking_ids(url):
    """Adds the Amazon tracking ID to a single URL if not present."""
    # Avoid adding tag if already present
    if 'tag=coffeeprism-20' not in url: # Replace with AMAZON_ASSOCIATE_TAG variable if implemented
         if '?' in url:
             # Check if there are already params, add with &
             if url.split('?')[-1]:
                 url += '&tag=coffeeprism-20' # Replace with AMAZON_ASSOCIATE_TAG variable if implemented
             else: # Handle case like "url?"
                 url += 'tag=coffeeprism-20' # Replace with AMAZON_ASSOCIATE_TAG variable if implemented
         else:
             url += '?tag=coffeeprism-20' # Replace with AMAZON_ASSOCIATE_TAG variable if implemented
    return url

# ---> UPDATED: 修改为使用搜索链接 <---
def validate_and_update_amazon_links(article_content):
    """
    解析文章内容中的潜在Amazon产品提及（在Markdown链接中），
    创建Amazon搜索链接（带有affiliate tag），替换原有链接。
    不再调用PA API。
    """
    print("正在更新文章中的Amazon链接为搜索链接...")

    updated_article_content = article_content
    links_processed = 0

    # 正则表达式匹配Markdown格式的Amazon链接
    # 捕获完整链接、链接文本（产品关键词）和URL
    amazon_link_pattern = re.compile(r'(\[([^\]]+)\]\((https?://(?:www\.)?amazon\.com[^\s\)]*)\))')

    # 在修改内容前查找所有匹配项
    matches = list(amazon_link_pattern.finditer(article_content))
    
    if not matches:
        print("未在文章中找到符合模式的Amazon链接占位符。")
        return article_content # 没有找到链接需要处理

    print(f"找到 {len(matches)} 个潜在的Amazon链接需要处理。")

    # 逐个处理匹配项，避免索引变化后的问题
    for match in matches:
        full_markdown_link = match.group(1)
        link_text = match.group(2).strip() # 使用链接文本作为关键词
        original_url = match.group(3) # 保留原始URL以供参考

        print(f"\n处理链接文本: '{link_text}' (来自: {original_url})")

        if not link_text:
            print("警告: 链接文本为空，跳过此占位符。")
            continue

        # 创建Amazon搜索链接
        try:
            encoded_product_name = urllib.parse.quote(link_text)
            
            # 创建带有affiliate tag的搜索链接
            search_url = f"https://www.amazon.com/s?k={encoded_product_name}&tag={AMAZON_ASSOCIATE_TAG}"
            
            # 创建新的markdown链接
            new_markdown_link = f"[{link_text}]({search_url})"
            
            # 替换原始链接
            if full_markdown_link in updated_article_content:
                updated_article_content = updated_article_content.replace(full_markdown_link, new_markdown_link, 1)
                print(f"已将链接更新为: {new_markdown_link}")
                links_processed += 1
            else:
                print(f"警告: 无法在当前内容中找到原始链接 '{full_markdown_link}' 进行替换。可能已被先前操作修改。")
                
        except Exception as e:
            print(f"处理链接 '{link_text}' 时发生错误: {e}")
            # 继续处理下一个链接

    print(f"\nAmazon链接处理完成。共处理/更新 {links_processed} 个链接。")
    return updated_article_content

##############################################################################
# 热点新闻抓取与分析文章生成
##############################################################################

# 多源新闻抓取关键词（中英文覆盖全球咖啡热点）
NEWS_QUERIES = [
    "coffee",
    "咖啡",
    "Starbucks OR 星巴克",
    "coffee beans price",
    "barista championship",
]


def fetch_google_news_rss(query, lang="en", max_items=10):
    """从 Google News RSS 抓取新闻（免费，无需API key）"""
    encoded_q = urllib.parse.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded_q}&hl={lang}&gl=US&ceid=US:{lang}"
    if lang == "zh":
        url = f"https://news.google.com/rss/search?q={encoded_q}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"

    try:
        resp = requests.get(url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; CoffeePrism/1.0)"
        })
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        items = []
        for item in root.findall(".//item")[:max_items]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            description = item.findtext("description", "")
            # 清理HTML标签
            description = re.sub(r'<[^>]+>', '', description).strip()
            items.append({
                "title": title,
                "link": link,
                "date": pub_date,
                "summary": description[:300]
            })
        return items
    except Exception as e:
        print(f"  抓取Google News失败 ({query}): {e}")
        return []


def fetch_coffee_news():
    """从多个来源汇总咖啡相关新闻"""
    print("\n📰 正在从多个来源抓取咖啡新闻...")
    all_news = []
    seen_titles = set()

    for query in NEWS_QUERIES:
        # 英文新闻
        items = fetch_google_news_rss(query, lang="en", max_items=8)
        for item in items:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_news.append(item)

    # 中文新闻单独抓取
    for query in ["咖啡 新闻", "咖啡 行业", "瑞幸 星巴克"]:
        items = fetch_google_news_rss(query, lang="zh", max_items=5)
        for item in items:
            if item["title"] not in seen_titles:
                seen_titles.add(item["title"])
                all_news.append(item)

    print(f"  共抓取 {len(all_news)} 条不重复新闻")
    return all_news


def evaluate_news_worthiness(news_items):
    """用 GPT-5.4 评估哪条新闻值得写深度分析，返回最佳候选或 None"""
    if not news_items:
        return None

    # 构建新闻摘要列表供AI评估
    news_digest = ""
    for i, item in enumerate(news_items[:30], 1):  # 最多评估30条
        news_digest += f"{i}. [{item['date'][:16] if item['date'] else 'N/A'}] {item['title']}\n   {item['summary'][:150]}\n\n"

    today = datetime.date.today().strftime("%Y-%m-%d")

    prompt = f"""你是一位资深咖啡行业分析师和内容策略专家。今天是 {today}。

以下是最新的咖啡相关新闻列表：

{news_digest}

请从中筛选出最适合写深度分析文章的**1条新闻**。筛选标准：
1. **时效性**：最近1-3天内的热点事件优先
2. **影响力**：对咖啡行业/消费者有重大影响的事件（价格波动、政策变化、品牌大事件、行业趋势）
3. **深度空间**：能从多个角度展开分析（经济、文化、技术、消费者影响）
4. **读者兴趣**：中国咖啡爱好者会关注的话题

如果没有值得深度分析的新闻（比如都是普通的产品发布或泛泛的行业报道），请直接回复：
SKIP

如果找到值得分析的新闻，请按以下JSON格式回复（不要添加任何其他文字）：
{{"news_index": 编号, "headline": "新闻标题", "angle": "建议的分析角度（一句话）", "why_trending": "为什么这是热点（一句话）", "target_keywords": ["关键词1", "关键词2", "关键词3"]}}"""

    print("  正在用 GPT-5.4 评估新闻热度...")
    result = call_linqai([
        {"role": "system", "content": "你是咖啡行业分析专家。只按要求的格式回复，不要多余解释。"},
        {"role": "user", "content": prompt}
    ])

    if not result:
        print("  AI评估失败")
        return None

    result = result.strip()

    # 检查是否跳过
    if "SKIP" in result.upper():
        print("  AI判断：当前无值得深度分析的热点新闻")
        return None

    # 解析JSON
    try:
        # 提取JSON部分（处理可能的多余文字）
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if not json_match:
            print(f"  无法解析AI回复: {result[:200]}")
            return None

        evaluation = json.loads(json_match.group())
        news_idx = evaluation.get("news_index", 1) - 1

        if 0 <= news_idx < len(news_items):
            selected = news_items[news_idx]
            selected["angle"] = evaluation.get("angle", "")
            selected["why_trending"] = evaluation.get("why_trending", "")
            selected["target_keywords"] = evaluation.get("target_keywords", [])
            print(f"  选中热点: {selected['title']}")
            print(f"  分析角度: {selected['angle']}")
            return selected

        print(f"  新闻索引越界: {news_idx}")
        return None

    except (json.JSONDecodeError, KeyError) as e:
        print(f"  解析AI评估结果失败: {e}")
        print(f"  原始回复: {result[:300]}")
        return None


def get_trending_article_prompt(news_item):
    """生成热点分析文章的提示词"""
    return f"""请为 Coffee Prism 网站撰写一篇针对以下咖啡行业热点新闻的**深度分析文章**。

## 新闻信息
- **标题**: {news_item['title']}
- **摘要**: {news_item['summary']}
- **来源链接**: {news_item['link']}
- **建议分析角度**: {news_item.get('angle', '多角度深度分析')}
- **目标关键词**: {', '.join(news_item.get('target_keywords', []))}

## 文章要求

这是一篇**热点深度分析**文章，不同于常规知识科普。要求：

### 输出格式
- 第一行以 `# ` 开头的标题（包含核心关键词，吸引眼球但不标题党）
- 不要输出 front matter 或 `---`

### 结构框架（3500-5000字）

**开篇速报（200字）**
- 用2-3句话概述新闻事件核心
- 立即点明这件事为什么重要，对谁有影响

**事件回顾与背景（400-600字）**
- 完整还原事件经过
- 补充必要的背景信息和行业上下文
- 引用具体数据和来源

**多角度深度分析（1500-2000字，3-4个H2章节）**
- 每个角度用独立的H2章节
- 分析角度建议：经济/市场影响、行业格局变化、消费者影响、中国市场关联
- 每个分析点都要有论据支撑（数据、案例、对比）
- 给出你的专业判断，不要只是罗列信息

**对中国咖啡市场/消费者的影响（400-600字）**
- 这条新闻对国内咖啡行业意味着什么
- 消费者应该关注什么
- 引用国内品牌（瑞幸、Manner、Seesaw、M Stand等）作为分析参照

**未来展望与预测（300-400字）**
- 基于当前趋势的合理预测
- 给出2-3个可能的发展场景

**常见问题解答（FAQ）**
- 4-6个问题，以H3格式
- 问题围绕读者最关心的实际影响
- 每个回答80-150字，先直答再展开

**专家观点/编辑点评（150-200字）**
- 以Coffee Prism编辑身份给出总结性观点

### 写作风格
- 新闻分析的专业语气，不是知识科普的轻松语气
- 有观点、有判断、有预测，而非四平八稳的报道
- 数据驱动，避免空泛的形容词
- 适当使用产品推荐链接（格式：[产品名](https://www.amazon.com/s?k=英文产品名)），但不要生硬

### 禁止事项
- 不要编造不存在的数据或引用来源
- 不要在标题中使用"震惊"、"重磅"等低质词
- 不要输出 front matter

现在请撰写这篇热点深度分析文章。"""


def generate_trending_article(news_item):
    """生成热点分析文章"""
    print(f"\n🔥 正在生成热点分析文章: {news_item['title'][:50]}...")

    messages = [
        {"role": "system", "content": get_system_prompt() + "\n\n你现在的角色是咖啡行业热点分析师，擅长将新闻事件转化为有深度、有洞察的分析文章。你的分析应该体现出专业的行业理解和独到的视角。"},
        {"role": "user", "content": get_trending_article_prompt(news_item)}
    ]

    article_content = call_linqai(messages)
    if not article_content:
        print("  热点文章生成失败")
        return None

    # 清理
    article_content = re.sub(r'<think>.*?</think>', '', article_content, flags=re.DOTALL).strip()
    article_content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', article_content, flags=re.DOTALL).strip()

    return article_content


def save_trending_article(article_content, news_item):
    """保存热点分析文章，使用专门的分类和标签"""
    if not article_content:
        return False

    # 构造一个与常规文章兼容的 topic_info
    keywords = news_item.get("target_keywords", ["咖啡", "行业分析"])
    topic_info = {
        "main_topic": "咖啡热点分析",
        "specific_topic": news_item["title"][:50]
    }

    # 复用 save_article，但在保存前修改一下分类
    title, title_line_indices = extract_title(article_content)
    if title == "默认标题":
        title = news_item["title"][:60]

    today = datetime.date.today().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    slug = slugify.slugify(title, separator='-', max_length=50)
    if not slug:
        slug = "trending-analysis"
    filename = f"{today}-{timestamp}-trending-{slug}-{unique_id}.md"

    content_dir = Path("content/posts")
    content_dir.mkdir(parents=True, exist_ok=True)
    filepath = content_dir / filename

    # 从文章提取FAQ和描述
    faq_items = extract_faq_from_content(article_content)
    seo_description = generate_seo_description(title, topic_info["specific_topic"], article_content)

    # 标签：使用AI建议的关键词 + 通用标签
    tags = keywords[:3] + ["咖啡热点", "行业分析"]
    tags = list(dict.fromkeys(tags))[:6]  # 去重，最多6个

    faq_json = json.dumps(faq_items, ensure_ascii=False) if faq_items else "[]"

    front_matter = f"""---
title: "{title}"
date: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
lastmod: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
draft: false
categories: ["咖啡热点分析"]
tags: {json.dumps(tags, ensure_ascii=False)}
description: "{seo_description}"
keywords: {json.dumps(tags[:5], ensure_ascii=False)}
author: "Coffee Prism"
faq: {faq_json}
slug: "{slug}"
canonicalURL: "https://www.coffeeprism.com/posts/{slug}/"
trending: true
news_source: "{news_item.get('link', '')}"
---

"""

    # 处理正文
    content_lines = article_content.strip().split('\n')
    processed_lines = [line for i, line in enumerate(content_lines) if i not in title_line_indices]
    processed_content = '\n'.join(processed_lines).strip()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + processed_content)
        print(f"  热点文章已保存至: {filepath}")
        return True
    except Exception as e:
        print(f"  保存热点文章失败: {e}")
        return False


def process_and_save_article(article_content, topic, label=""):
    """文章后处理通用流程：质量检查 -> Amazon链接 -> 保存"""
    title, _ = extract_title(article_content)

    try:
        check_content_quality(article_content, title, topic['specific_topic'])
    except Exception as e:
        print(f"⚠️  质量检查时出错 (非致命): {e}")

    try:
        print("\n🔗 处理Amazon链接...")
        article_content = validate_and_update_amazon_links(article_content)
    except Exception as e:
        print(f"⚠️  验证/更新 Amazon 链接时出错 (非致命): {e}")

    print("\n💾 保存文章...")
    success = save_article(article_content, topic)
    if success:
        print(f"✅ {label}文章生成并保存成功！")
    else:
        print(f"❌ {label}文章保存失败")
    return success


def main():
    print("开始自动文章生成流程...")

    random.seed(time.time())
    articles_saved = 0

    # ========== 第一阶段：热点新闻分析 ==========
    print("\n" + "=" * 60)
    print("=== 第一阶段：热点新闻抓取与分析 ===")
    print("=" * 60)

    try:
        news_items = fetch_coffee_news()
        trending = evaluate_news_worthiness(news_items)

        if trending:
            print(f"\n🔥 发现值得分析的热点: {trending['title'][:60]}")
            trending_content = generate_trending_article(trending)

            if trending_content:
                # 处理Amazon链接
                try:
                    trending_content = validate_and_update_amazon_links(trending_content)
                except Exception as e:
                    print(f"⚠️  处理热点文章链接时出错 (非致命): {e}")

                # 保存热点文章
                if save_trending_article(trending_content, trending):
                    articles_saved += 1
                    print("✅ 热点分析文章发布成功！")
                else:
                    print("❌ 热点文章保存失败")
            else:
                print("❌ 热点文章生成失败")
        else:
            print("\n📋 今日无重大热点，跳过热点分析")

    except Exception as e:
        print(f"⚠️  热点新闻流程出错 (非致命): {e}")
        traceback.print_exc()

    # ========== 第二阶段：常规主题文章 ==========
    print("\n" + "=" * 60)
    print("=== 第二阶段：常规主题文章生成 ===")
    print("=" * 60)

    topics = select_random_coffee_topics(2)

    for i, topic in enumerate(topics, 1):
        print(f"\n{'='*60}")
        print(f"--- 生成第 {i} 篇常规文章 ---")
        print(f"主题: {topic['main_topic']} - {topic['specific_topic']}")
        print(f"{'='*60}")

        article_content = generate_article(topic)
        if not article_content:
            print(f"❌ 无法生成关于「{topic['main_topic']}：{topic['specific_topic']}」的文章，跳过")
            continue

        print(f"\n✅ 文章生成成功！开始后处理...")
        if process_and_save_article(article_content, topic, label=f"第{i}篇"):
            articles_saved += 1

    print(f"\n{'='*60}")
    print(f"自动文章生成完成！共保存 {articles_saved} 篇文章。")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 