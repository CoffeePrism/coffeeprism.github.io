#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
# import requests # No longer needed for API call
import datetime
import re
import json
import time
import uuid
import random
from pathlib import Path
import slugify
from openai import OpenAI # Still use the openai library

# --- Configuration ---
# Use environment variable for NVIDIA API key
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
# Site info is not needed for NVIDIA API headers
# YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "https://www.coffeeprism.com")
# YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "Coffee Prism")

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
    """从文章内容中提取标题"""
    lines = article_content.strip().split('\n')
    if not lines:
        return "默认标题"
        
    title = lines[0].strip()
    
    # --- Clean up logic ---
    # Remove prefixes like "#", "**", "标题："
    prefixes_to_remove = ["#", "**", "标题：", "标题:"]
    for prefix in prefixes_to_remove:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()
            
    # Remove trailing "**"
    if title.endswith("**"):
        title = title[:-2].strip()
        
    # Strip extra whitespace or markers again
    title = title.strip("* \t\n\r")
    # --- Clean up logic ends ---
    
    # Remove surrounding quotes
    if (title.startswith('"') and title.endswith('"')) or (title.startswith("'") and title.endswith("'")):
        title = title[1:-1]
        
    # Provide default title if empty after cleaning
    if not title:
        return "默认标题"
        
    return title

def save_article(article_content, topic_info):
    """保存生成的文章到Hugo内容目录"""
    if not article_content:
        print("错误: 没有要保存的文章内容")
        return False
    
    try:
        # Create content directory if it doesn't exist
        content_dir = Path("content/posts")
        content_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract title
        title = extract_title(article_content)
        
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
        
        # Process article content - remove original title line if present
        content_lines = article_content.strip().split('\n')
        # Improve title removal logic: check if first line *is* the cleaned title or starts with '#'
        cleaned_first_line = content_lines[0].strip()
        if cleaned_first_line.lstrip('#').strip() == title or (cleaned_first_line.startswith('"') and cleaned_first_line.endswith('"') and cleaned_first_line[1:-1] == title):
             content_lines = content_lines[1:]
        processed_content = '\n'.join(content_lines).strip()
        
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

# ---> NEW: Function for validating and updating Amazon links using PA API
def validate_and_update_amazon_links(article_content):
    """
    Parses article content for Amazon links, validates ASINs using PA API,
    and updates links accordingly. Adds tracking tags.
    Requires PA API credentials and library setup.
    """
    print("正在验证和更新 Amazon 链接...")

    updated_article_content = article_content
    
    # Regex to find Markdown links pointing to Amazon product pages (extract ASIN)
    # Example: [Product Name](https://www.amazon.com/dp/B0EXAMPLE1/...)
    # Example: [Product Name](https://www.amazon.com/Some-Product-Name/dp/B0EXAMPLE2?...)
    amazon_link_pattern = re.compile(r'(\[([^\]]+)\]\((https?://(?:www\.)?amazon\.com/(?:[^/]+/)?dp/([A-Z0-9]{10})[^\s\)]*)\))')

    links_to_process = amazon_link_pattern.finditer(article_content)
    asins_to_check = {} # Store {asin: [list_of_full_markdown_links]}

    for match in links_to_process:
        full_markdown_link = match.group(1)
        # product_name = match.group(2) # Can be used if needed
        original_url = match.group(3)
        asin = match.group(4)
        
        if asin not in asins_to_check:
            asins_to_check[asin] = []
        asins_to_check[asin].append({"full_link": full_markdown_link, "original_url": original_url})

    if not asins_to_check:
        print("未在文章中找到需要验证的 Amazon 产品链接。")
        # Still ensure non-product Amazon links get tracking ID
        misc_pattern = r'(\(https?://(?:www\.)?amazon\.com/[^\s\)]+\))' # Generic Amazon link
        def replace_misc_link(match):
            url_part = match.group(1)
            original_url = url_part[1:-1]
            # Avoid processing product links again if pattern overlaps
            if '/dp/' in original_url: 
                return url_part 
            updated_url = add_amazon_tracking_ids(original_url)
            return f"({updated_url})"
        return re.sub(misc_pattern, replace_misc_link, article_content)

    print(f"找到 {len(asins_to_check)} 个独特的 ASIN 需要通过 PA API 验证: {list(asins_to_check.keys())}")

    # ---> Placeholder: PA API Call Implementation
    # try:
    #     # Prepare GetItems request for all unique ASINs
    #     get_items_request = GetItemsRequest(
    #         partner_tag=AMAZON_ASSOCIATE_TAG,
    #         partner_type=PartnerType.ASSOCIATES,
    #         marketplace=AMAZON_MARKETPLACE,
    #         condition=Condition.NEW, # Or desired condition
    #         item_ids=list(asins_to_check.keys()),
    #         resources=[
    #             GetItemsResource.ITEMINFO_TITLE, # Get title for verification
    #             GetItemsResource.OFFERS_LISTINGS_PRICE, # Check availability/price
    #             GetItemsResource.IMAGES_PRIMARY_SMALL # Optional: Get image
    #             # Add more resources as needed
    #         ]
    #     )
    #     
    #     api_response = api_instance.get_items(get_items_request)
    #     
    #     valid_items = {}
    #     if api_response.items_result and api_response.items_result.items:
    #         for item in api_response.items_result.items:
    #             # Basic validation: Check if item has a title and price/offer info
    #             if item.item_info and item.item_info.title and item.offers and item.offers.listings:
    #                 valid_items[item.asin] = {"url": item.detail_page_url} # Store valid URL
    #             else:
    #                 print(f"警告: ASIN {item.asin} 在 PA API 响应中信息不完整或无货。")
    #     
    #     if api_response.errors:
    #        for error in api_response.errors:
    #            print(f"PA API 错误: Code={error.code}, Message={error.message}")
    #            # Decide how to handle ASINs associated with errors
    #
    # except ApiException as e:
    #     print(f"调用 Amazon PA API 时发生错误: {e}")
    #     print("无法验证链接，将仅尝试添加跟踪ID。")
    #     # Fallback logic
    #     pattern = r'(\(https?://(?:www\.)?amazon\.com/[^\s\)]+\))'
    #     def replace_link_simple_error(match):
    #         url_part = match.group(1)
    #         original_url = url_part[1:-1]
    #         updated_url = add_amazon_tracking_ids(original_url)
    #         return f"({updated_url})"
    #     return re.sub(pattern, replace_link_simple_error, article_content)
    #
    # except Exception as e:
    #     print(f"处理 PA API 响应时发生未知错误: {e}")
    #     # Fallback logic might be needed here too

    # ---> Placeholder: Update links in the article based on validation results
    for asin, link_infos in asins_to_check.items():
        for link_info in link_infos:
            full_markdown_link = link_info["full_link"]
            original_url = link_info["original_url"]
            
            # ---> Placeholder: Use 'valid_items' from API call
            # if asin in valid_items:
            #     # ASIN is valid, use the URL from PA API (which should be correct)
            #     validated_url = valid_items[asin]['url']
            #     # Ensure tracking tag is added to the validated URL
            #     final_url = add_amazon_tracking_ids(validated_url)
            #     # Replace the original URL part within the full markdown link
            #     updated_markdown_link = full_markdown_link.replace(original_url, final_url)
            #     updated_article_content = updated_article_content.replace(full_markdown_link, updated_markdown_link)
            #     print(f"已验证并更新 ASIN {asin} 的链接。")
            # else:
            #     # ASIN is invalid, unavailable, or caused an error
            #     print(f"警告: ASIN {asin} 无效或不可用。从文章中移除链接: {full_markdown_link}")
            #     # Option 1: Remove the whole markdown link
            #     updated_article_content = updated_article_content.replace(full_markdown_link, f"[链接失效: {asin}]") # Or just remove entirely
            #     # Option 2: Keep the link but maybe add a note (less ideal for 404s)
            #     # final_url = add_amazon_tracking_ids(original_url) # Add tag anyway
            #     # updated_markdown_link = full_markdown_link.replace(original_url, final_url + " (可能失效)")
            #     # updated_article_content = updated_article_content.replace(full_markdown_link, updated_markdown_link)

            # ---> Fallback/Demo logic (REMOVE THIS WHEN PA API IS IMPLEMENTED):
            # Just add tracking ID without validation for now
            print(f"注意：PA API 验证未实现。仅为 ASIN {asin} 添加跟踪 ID。")
            final_url = add_amazon_tracking_ids(original_url)
            if final_url != original_url:
                updated_markdown_link = full_markdown_link.replace(original_url, final_url)
                updated_article_content = updated_article_content.replace(full_markdown_link, updated_markdown_link)
            # --- End Fallback ---

    # Final pass for any non-product Amazon links missed
    misc_pattern = r'(\(https?://(?:www\.)?amazon\.com/[^\s\)]+\))' 
    def replace_misc_link_final(match):
        url_part = match.group(1)
        original_url = url_part[1:-1]
        if '/dp/' in original_url and any(asin in original_url for asin in asins_to_check): # Avoid reprocessing validated links
             return url_part 
        updated_url = add_amazon_tracking_ids(original_url)
        return f"({updated_url})"
    updated_article_content = re.sub(misc_pattern, replace_misc_link_final, updated_article_content)

    return updated_article_content
# --- End NEW Function ---

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