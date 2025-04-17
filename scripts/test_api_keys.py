#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import json

def test_newsapi_key(api_key):
    """测试NewsAPI密钥是否有效"""
    print("\n=== 测试 NewsAPI 密钥 ===")
    if not api_key:
        print("错误: NewsAPI 密钥未提供")
        return False
    
    print(f"使用密钥: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    url = f"https://newsapi.org/v2/everything?q=coffee&sortBy=publishedAt&language=en&pageSize=1&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') == 'ok':
            article_count = len(data.get('articles', []))
            print(f"API请求成功! 返回了 {article_count} 篇文章")
            return True
        else:
            print(f"API响应错误: {data.get('message', '未知错误')}")
            print(f"完整响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"状态码: {e.response.status_code}")
            try:
                print(f"响应内容: {e.response.text}")
            except:
                print("无法读取响应内容")
        return False

def test_openai_key(api_key):
    """测试OpenAI API密钥是否有效"""
    print("\n=== 测试 OpenAI API 密钥 ===")
    if not api_key:
        print("错误: OpenAI API 密钥未提供")
        return False
    
    print(f"使用密钥: {api_key[:4]}...{api_key[-4:] if len(api_key) > 8 else ''}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": "Hello, this is a test message."}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0]['message']['content']
            print(f"API请求成功! 响应: '{content}'")
            return True
        else:
            print(f"API响应格式不正确: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"状态码: {e.response.status_code}")
            try:
                print(f"响应内容: {e.response.text}")
            except:
                print("无法读取响应内容")
        return False

def main():
    print("=== API 密钥测试工具 ===")
    print("注意: 此工具将测试环境变量中设置的 NewsAPI 和 OpenAI API 密钥")
    
    # 从环境变量获取密钥
    newsapi_key = os.getenv("NEWSAPI_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # 测试 NewsAPI 密钥
    newsapi_success = test_newsapi_key(newsapi_key)
    
    # 测试 OpenAI API 密钥
    openai_success = test_openai_key(openai_api_key)
    
    # 总结
    print("\n=== 测试结果汇总 ===")
    print(f"NewsAPI 密钥: {'有效 ✓' if newsapi_success else '无效 ✗'}")
    print(f"OpenAI API 密钥: {'有效 ✓' if openai_success else '无效 ✗'}")
    
    if not newsapi_success or not openai_success:
        print("\n如何设置 API 密钥:")
        print("临时设置（仅当前终端会话）:")
        print("  export NEWSAPI_KEY='您的密钥'")
        print("  export OPENAI_API_KEY='您的密钥'")
        print("\n永久设置（添加到您的 shell 配置文件，如 ~/.zshrc 或 ~/.bashrc）:")
        print("  echo 'export NEWSAPI_KEY=\"您的密钥\"' >> ~/.zshrc")
        print("  echo 'export OPENAI_API_KEY=\"您的密钥\"' >> ~/.zshrc")
        print("  source ~/.zshrc")

if __name__ == "__main__":
    main() 