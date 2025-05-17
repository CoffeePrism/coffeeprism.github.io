#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
import re
import json
import time
import uuid
import random
from pathlib import Path
import slugify
from openai import OpenAI

# --- Configuration ---
# Use environment variable for NVIDIA API key
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")

# Check API key
if not NVIDIA_API_KEY:
    print("错误: NVIDIA_API_KEY 环境变量未设置。请设置后再运行此脚本。")
    exit(1)

# Initialize OpenAI Client pointing to NVIDIA API
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = NVIDIA_API_KEY
)

# Define the NVIDIA model to use
MODEL_NAME = "deepseek-ai/deepseek-r1" # Changed to NVIDIA model

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
    """使用 NVIDIA API 生成咖啡相关文章"""
    main_topic = topic_info["main_topic"]
    specific_topic = topic_info["specific_topic"]
    
    print(f"正在生成关于「{main_topic}：{specific_topic}」的文章 (使用模型: {MODEL_NAME})...")
    
    if not NVIDIA_API_KEY:
        print("错误: 未设置NVIDIA_API_KEY环境变量")
        return None
    
    prompt = f"""你是一位资深咖啡专家和作家。请创作一篇关于「{main_topic}：{specific_topic}」的中文文章，内容约1200-1500字，并提供一个有吸引力的标题。文章应面向中国咖啡爱好者，风格清新专业。

这应该是一篇高质量的niche文章，内容深入、专业且具有教育意义。请确保文章是原创的、信息丰富的，并且对咖啡爱好者有实际价值。

如果文章中涉及到具体的咖啡产品（如咖啡机、咖啡豆、咖啡杯等），请适当添加亚马逊链接，格式为[产品名称](https://www.amazon.com/s?k=产品名称)。每篇文章可以包含2-3个相关产品推荐。注意不要使用ASIN直接链接，而是使用搜索链接。

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

    try:
        # Use the initialized client to create completion with streaming
        completion_stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"user","content": prompt}],
            temperature=0.6, # Adjusted temperature
            top_p=0.7,       # Adjusted top_p
            max_tokens=4096, # Adjusted max_tokens
            stream=True      # Enable streaming
        )

        # Process the stream
        article_content_parts = []
        for chunk in completion_stream:
            if chunk.choices[0].delta.content is not None:
                article_content_parts.append(chunk.choices[0].delta.content)

        article_content = "".join(article_content_parts)

        if not article_content:
             print("错误: API 流未返回任何内容")
             return None

        # --- NEW: Remove <think> blocks ---
        # Use re.DOTALL so '.' matches newline characters as well
        article_content = re.sub(r'<think>.*?</think>', '', article_content, flags=re.DOTALL).strip() 
        # --- End NEW ---

        return article_content
        
    except Exception as e:
        print(f"调用 NVIDIA API 时发生异常: {e}")
        # ---> 新增: 打印详细的回溯信息
        import traceback
        print("-- Traceback --")
        traceback.print_exc()
        print("-- End Traceback --")
        return None

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
        
        # Determine category and tags
        category = topic_info["main_topic"]
        # Attempt to extract a more relevant tag, fallback to specific topic
        potential_tag = topic_info["specific_topic"].split("的")[0] if "的" in topic_info["specific_topic"] else topic_info["specific_topic"]
        potential_tag = potential_tag.split("与")[0] if "与" in potential_tag else potential_tag # Handle "A与B" cases
        tags = [potential_tag.strip()]
        
        # Create Front Matter
        # Use ensure_ascii=False for Chinese characters in tags JSON
        front_matter = f"""---
title: "{title}"
date: {today}
draft: false
categories: ["{category}"]
tags: {json.dumps(tags, ensure_ascii=False)}
description: "关于{topic_info['specific_topic']}的深度探讨，为咖啡爱好者提供专业知识和实用指南。"
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
            # 对产品名称进行URL编码
            import urllib.parse
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

def main():
    print("开始自动文章生成流程...")
    
    # Set random seed
    random.seed(time.time())
    
    # Select random topics
    topics = select_random_coffee_topics(2) # Generate 2 articles
    
    # Generate and save articles
    articles_saved = 0
    for i, topic in enumerate(topics, 1):
        print(f"\n=== 生成第 {i} 篇文章 ===")
        
        # Generate article
        article_content = generate_article_with_openai(topic)
        if not article_content:
            print(f"无法生成关于「{topic['main_topic']}：{topic['specific_topic']}」的文章，跳过")
            continue
        
        # --- UPDATED: Validate links and add tracking ID ---
        try:
             # Replace call to add_amazon_tracking_ids
             article_content = validate_and_update_amazon_links(article_content)
        except Exception as e:
             print(f"验证/更新 Amazon 链接时出错 (非致命): {e}")
             # Optionally, add a fallback or just log
        # --- End UPDATED ---
        
        # Save article
        success = save_article(article_content, topic)
        if success:
            print(f"第 {i} 篇文章生成并保存成功")
            articles_saved += 1
        else:
            print(f"第 {i} 篇文章保存失败")
    
    print(f"\n自动文章生成完成！成功保存 {articles_saved} 篇文章。")

if __name__ == "__main__":
    main() 