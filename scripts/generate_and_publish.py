#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import content_checks  # noqa: E402  (scripts/content_checks.py)

# --- Configuration ---
# 使用环境变量获取Amazon Associate Tag
AMAZON_ASSOCIATE_TAG = os.getenv("AMAZON_ASSOCIATE_TAG", "coffeeprism-20")

# --- LLM providers ---
# 历史教训：2026-04 起改用的免费无鉴权代理 x.linq.ai 在 2026-09 下旬开始
# 返回 500、2026-10 底彻底不可达，而脚本仍 exit 0 —— CI 连续近两个月
# "绿灯" 但 0 篇产出。现在改为：
#   1. 只用有 API key 的 OpenAI 兼容接口，按顺序回退（自定义 → OpenRouter → NVIDIA）
#   2. 鉴权/余额/模型不存在等不可恢复错误 → 本次运行直接跳过该 provider
#   3. 连接失败快速熔断（不再 3 次 × 120s 地干等）
#   4. 一篇都没生成 → 进程非 0 退出，让 Actions 标红并发邮件
DEFAULT_OPENROUTER_MODEL = "openai/gpt-5.4"   # 与 2026-04 起的存量文章同一模型，文风连续
DEFAULT_NVIDIA_MODEL = "z-ai/glm-5.3-flash"   # NVIDIA 免费额度兜底
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS") or 16000)
LLM_CONNECT_TIMEOUT = 15
LLM_READ_TIMEOUT = int(os.getenv("LLM_READ_TIMEOUT") or 600)


def _model_list(value, default):
    """模型变量支持逗号分隔多个，按顺序回退（免费模型随时可能被限流/下架）。"""
    models = [m.strip() for m in (value or "").split(",") if m.strip()]
    return models or [m.strip() for m in default.split(",") if m.strip()]


def _build_providers():
    """按优先级组装可用的 (provider, model) 列表（只收录配置了 key 的）。"""
    configs = []
    if os.getenv("LLM_API_KEY") and os.getenv("LLM_BASE_URL"):
        configs.append(("custom", os.environ["LLM_BASE_URL"].rstrip("/"), os.environ["LLM_API_KEY"],
                        _model_list(os.getenv("LLM_MODEL"), DEFAULT_OPENROUTER_MODEL), {}))
    if os.getenv("OPENROUTER_API_KEY"):
        configs.append(("openrouter", "https://openrouter.ai/api/v1", os.environ["OPENROUTER_API_KEY"],
                        _model_list(os.getenv("OPENROUTER_MODEL"), DEFAULT_OPENROUTER_MODEL),
                        {"HTTP-Referer": "https://www.coffeeprism.com", "X-Title": "Coffee Prism"}))
    if os.getenv("NVIDIA_API_KEY"):
        configs.append(("nvidia", "https://integrate.api.nvidia.com/v1", os.environ["NVIDIA_API_KEY"],
                        _model_list(os.getenv("NVIDIA_MODEL"), DEFAULT_NVIDIA_MODEL), {}))
    providers = []
    for name, base_url, api_key, models, headers in configs:
        for model in models:
            providers.append({
                "name": name, "base_url": base_url, "api_key": api_key, "model": model,
                "headers": headers, "dead": False, "conn_failures": 0, "send_max_tokens": True,
            })
    return providers


PROVIDERS = _build_providers()
# 给日志/提示用的"当前模型"名（第一个可用 provider 的模型）
MODEL_NAME = PROVIDERS[0]["model"] if PROVIDERS else "(未配置)"


def describe_providers():
    if not PROVIDERS:
        return "❌ 未配置任何 LLM key（需要 OPENROUTER_API_KEY / NVIDIA_API_KEY / LLM_API_KEY+LLM_BASE_URL 之一）"
    return " → ".join(f"{p['name']}:{p['model']}" for p in PROVIDERS)


def _short(text, n=300):
    text = re.sub(r'\s+', ' ', text or '')
    return text[:n]


def call_llm(messages, max_retries=3):
    """调用 OpenAI 兼容的 chat/completions 接口，按 provider 顺序回退。
    成功返回文本，全部失败返回 None。"""
    for p in PROVIDERS:
        if p["dead"]:
            continue
        for attempt in range(1, max_retries + 1):
            payload = {"model": p["model"], "messages": messages, "temperature": 0.7}
            if p["send_max_tokens"]:
                payload["max_tokens"] = LLM_MAX_TOKENS
            headers = {"Authorization": f"Bearer {p['api_key']}", "Content-Type": "application/json", **p["headers"]}
            tag = f"[{p['name']}:{p['model']}] (尝试 {attempt}/{max_retries})"
            try:
                resp = requests.post(f"{p['base_url']}/chat/completions", headers=headers, json=payload,
                                     timeout=(LLM_CONNECT_TIMEOUT, LLM_READ_TIMEOUT))
            except (requests.ConnectionError, requests.Timeout) as e:
                p["conn_failures"] += 1
                print(f"  ⚠️  {tag} 网络错误: {_short(str(e), 160)}")
                if p["conn_failures"] >= 3:
                    print(f"  🔌 {p['name']} 连续 {p['conn_failures']} 次网络失败，本次运行熔断")
                    p["dead"] = True
                    break
                time.sleep(5 * attempt)
                continue

            if resp.status_code == 200:
                try:
                    data = resp.json()
                    content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
                except ValueError:
                    content = ""
                p["conn_failures"] = 0
                if content.strip():
                    return content
                print(f"  ⚠️  {tag} 返回空内容: {_short(resp.text, 200)}")
                time.sleep(3)
                continue

            body = _short(resp.text)
            if resp.status_code == 400 and p["send_max_tokens"] and "max" in body.lower() and "token" in body.lower():
                print(f"  ⚠️  {tag} 不接受 max_tokens={LLM_MAX_TOKENS}，去掉该参数重试: {body}")
                p["send_max_tokens"] = False
                continue
            if resp.status_code in (401, 403):
                # key 无效：同一个 key 下的所有模型都不用再试
                print(f"  ❌ {tag} HTTP {resp.status_code}，key 无效，本次运行跳过 {p['name']} 的全部模型: {body}")
                for q in PROVIDERS:
                    if q["name"] == p["name"]:
                        q["dead"] = True
                break
            if resp.status_code in (400, 402, 404):
                # 余额不足（付费模型）/ 模型不存在或已下架 / 请求格式不被接受：
                # 只跳过这个模型，同 key 的其他模型（如免费模型）继续试
                print(f"  ❌ {tag} HTTP {resp.status_code}，本次运行跳过该模型: {body}")
                p["dead"] = True
                break
            # 429 / 5xx / 其它：退避重试
            print(f"  ⚠️  {tag} HTTP {resp.status_code}: {body}")
            time.sleep(10 * attempt)
    return None


# 兼容旧名字（scripts/ 里其他脚本或旧分支可能还在引用）
call_linqai = call_llm


# --- 标题相似度（用于选题去重 / 近似重复标题拦截） ---
# 以「规范化标题的汉字二元组」做包含度：|A∩B| / min(|A|,|B|)。
# 在现有 756 个标题上校准过：>=0.6 基本都是同一选题换说法
# （如「咖啡节与展会介绍：从入门到精通的实用宝典」vs「…完全攻略」）。
_GENERIC_TITLE_WORDS = [
    "从入门到精通", "你需要知道的", "完全指南", "完整指南", "实用指南", "实用宝典", "终极指南",
    "深度解析", "深度指南", "完全攻略", "全攻略", "实战技巧", "实战指南", "攻略", "指南", "技巧",
    "详解", "解析", "入门", "进阶", "全面", "揭秘", "探索", "解码", "秘密", "密码", "最佳", "完美",
    "如何", "为什么", "一文读懂", "咖啡",
]
DUP_TITLE_THRESHOLD = 0.6      # 成稿标题与已有标题的包含度上限
DUP_CANDIDATE_THRESHOLD = 0.5  # 选题阶段更严格


def _norm_title(t):
    t = re.sub(r'[^\w]', '', t or '')
    for w in _GENERIC_TITLE_WORDS:
        t = t.replace(w, '')
    return t


def _bigrams(s):
    if len(s) < 2:
        return {s} if s else set()
    return {s[i:i + 2] for i in range(len(s) - 1)}


def title_similarity(a, b):
    A, B = _bigrams(_norm_title(a)), _bigrams(_norm_title(b))
    if not A or not B:
        return 0.0
    return len(A & B) / min(len(A), len(B))


def most_similar_title(title, existing_titles):
    """返回 (相似度, 最相近的已有标题)。"""
    best = (0.0, "")
    for t in existing_titles:
        s = title_similarity(title, t)
        if s > best[0]:
            best = (s, t)
    return best


def load_existing_posts():
    """读取全部已发布文章的 (title, category, date)。用 front matter，
    不用文件 mtime —— CI 每次 checkout 后所有文件 mtime 都是"现在"。"""
    posts = []
    for p in Path("content/posts").glob("*.md"):
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(1500)
        except Exception:
            continue
        tm = re.search(r'^title:\s*"?(.*?)"?\s*$', head, re.M)
        cm = re.search(r'^categories:\s*\[\s*"([^"]+)"', head, re.M)
        dm = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', head, re.M)
        if tm and tm.group(1):
            posts.append({
                "title": tm.group(1).replace('\\"', '"'),
                "category": cm.group(1) if cm else "",
                "date": dm.group(1) if dm else "",
            })
    return posts


def unique_slug(slug, fallback_suffix):
    """slug 撞车时追加后缀。历史上 68 篇文章共用 18 个 slug（同一选题的标题
    前缀相同 → slugify 截断到 50 字符后完全一样），Hugo 输出到同一路径，
    50 篇被互相覆盖、首页卡片标题与打开的文章对不上。"""
    taken = set()
    for p in Path("content/posts").glob("*.md"):
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(2500)
        except Exception:
            continue
        m = re.search(r'^slug:\s*"?([^"\n]+?)"?\s*$', head, re.M)
        taken.add(m.group(1) if m else p.stem)
    if slug not in taken:
        return slug
    return f"{slug}-{fallback_suffix}"


def yaml_str(s):
    """front matter 字符串安全转义（JSON 字符串是合法 YAML）。
    之前用 f-string 直接拼 "..."，标题/摘要里一旦出现英文双引号就会让 Hugo 构建失败。"""
    return json.dumps(s or "", ensure_ascii=False)

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

def get_subtopic_coverage(existing_posts):
    """统计每个 (类目, 子主题) 已有多少篇近似文章（全量、按标题相似度）。

    旧实现有两个 bug，导致选题池实际上只剩 9 个子主题、反复产出近似重复文章：
      1. 用文件 mtime 判断"最近 60 天"，CI checkout 后所有文件都算最近；
      2. 用 split("与") 取关键短语，「咖啡与X」类子主题只剩「咖啡」，永远判不中。
    """
    coverage = {}
    for topic in COFFEE_TOPICS:
        cat_titles = [p["title"] for p in existing_posts if p["category"] == topic["title"]]
        for sub in topic["subtopics"]:
            coverage[(topic["title"], sub)] = sum(
                1 for t in cat_titles if title_similarity(sub, t) >= DUP_CANDIDATE_THRESHOLD)
    return coverage


def get_category_counts(days=14):
    """统计最近 N 天每个类目发了多少篇文章（按 frontmatter date）。
    用于平衡选题——优先给冷门类目补内容。"""
    import datetime as _dt
    cutoff = _dt.date.today() - _dt.timedelta(days=days)
    counts = {t["title"]: 0 for t in COFFEE_TOPICS}
    for p in Path("content/posts").glob("*.md"):
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(800)
        except Exception:
            continue
        dm = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', head, re.M)
        if not dm:
            continue
        try:
            d = _dt.date.fromisoformat(dm.group(1))
        except ValueError:
            continue
        if d < cutoff:
            continue
        cm = re.search(r'^categories:\s*\["([^"]+)"', head, re.M)
        if cm and cm.group(1) in counts:
            counts[cm.group(1)] += 1
    return counts


def select_random_coffee_topics(count, existing_posts):
    """选 count 个「种子」(category, subtopic)：
    1. 不同类目优先（同一次运行不出两篇同类目）
    2. 优先最近 14 天发文最少的类目（保证主题平衡）
    3. 类目内优先已有近似文章最少的子主题

    注意：83 个子主题现在都已有文章，种子只决定方向，真正的选题由
    plan_fresh_topic() 在种子下找一个站内还没写过的长尾角度。
    """
    coverage = get_subtopic_coverage(existing_posts)
    cat_counts = get_category_counts(days=14)
    print(f"📊 最近 14 天类目分布: {dict(sorted(cat_counts.items(), key=lambda x: -x[1]))}")
    uncovered = sum(1 for v in coverage.values() if v == 0)
    print(f"📋 子主题覆盖：{len(coverage)} 个中 {uncovered} 个尚无近似文章")

    categories = [t["title"] for t in COFFEE_TOPICS]
    random.shuffle(categories)
    categories.sort(key=lambda c: cat_counts.get(c, 0))  # 冷门类目在前（同数量时随机）

    selected = []
    for cat in categories[:count]:
        subs = next(t["subtopics"] for t in COFFEE_TOPICS if t["title"] == cat)
        min_cov = min(coverage[(cat, s)] for s in subs)
        least = [s for s in subs if coverage[(cat, s)] <= min_cov + 1]
        sub = random.choice(least)
        selected.append({"main_topic": cat, "specific_topic": sub, "seed": sub,
                         "seed_coverage": coverage[(cat, sub)]})
    return selected


def plan_fresh_topic(seed_topic, existing_posts, n_candidates=6):
    """在种子子主题下，让 LLM 提出站内还没覆盖的具体长尾选题，
    过滤掉与已有标题近似的，返回第一个可用选题；失败返回 None。"""
    cat = seed_topic["main_topic"]
    seed = seed_topic["specific_topic"]
    all_titles = [p["title"] for p in existing_posts]
    cat_titles = [p["title"] for p in existing_posts if p["category"] == cat]
    # 种子本身还没写过就直接用
    if seed_topic.get("seed_coverage", 1) == 0:
        return dict(seed_topic)

    listing = "\n".join(f"- {t}" for t in cat_titles[-120:])
    prompt = f"""你是 Coffee Prism（中文咖啡知识站）的选题编辑。今天是 {datetime.date.today().isoformat()}。
类目：{cat}
种子方向：{seed}

本站这个类目下已经发布的文章标题如下（新选题不能与它们重复，换个说法也不行）：
{listing}

请提出 {n_candidates} 个新的中文长尾选题，要求：
1. 每个选题是真实读者会在搜索引擎或 AI 助手里问的具体问题/需求（例如「X 和 Y 哪个好」「X 怎么选」「新手做 X 的步骤」「X 失败的原因」），优先：购买决策、具体操作方法、问题排查；
2. 与上面已有标题的核心关键词或搜索意图明显不同；
3. 与种子方向相关，但可以更具体、更细分；
4. 每个选题 6-20 个汉字，会直接作为文章的主关键词使用，不要书名号和标点。

只输出一个 JSON 字符串数组，不要任何其它文字，例如：["选题一", "选题二"]"""

    raw = call_llm([
        {"role": "system", "content": "你是严谨的中文内容选题编辑。只按要求的格式输出。"},
        {"role": "user", "content": prompt},
    ])
    if not raw:
        print("  ❌ 选题规划失败（LLM 无响应）")
        return None
    m = re.search(r'\[.*\]', _strip_thinking(raw), re.S)
    try:
        candidates = json.loads(m.group(0)) if m else []
    except json.JSONDecodeError:
        candidates = []
    candidates = [c.strip().strip('《》"“”') for c in candidates if isinstance(c, str) and c.strip()]
    if not candidates:
        print(f"  ❌ 选题规划结果无法解析: {_short(raw, 200)}")
        return None

    for cand in candidates:
        score, near = most_similar_title(cand, all_titles)
        if score >= DUP_CANDIDATE_THRESHOLD:
            print(f"  ↩️  跳过选题「{cand}」：与已有「{near}」相似度 {score:.2f}")
            continue
        print(f"  ✅ 新选题「{cand}」（最相近已有标题相似度 {score:.2f}）")
        return {"main_topic": cat, "specific_topic": cand, "seed": seed}
    print("  ❌ 所有候选选题都与已有文章近似，本篇跳过")
    return None


# Topic → pillar URL mapping. New articles get a pillar link injected at top.
# Cover all categories used in the wild (验证：grep ^categories: content/posts/)
PILLAR_BY_CATEGORY = {
    # 直接对应
    "咖啡豆种类": ("/coffee-beans/", "咖啡豆完全指南"),
    "咖啡制作技巧": ("/brewing-methods/", "咖啡冲煮方法完全指南"),
    "咖啡设备与器具": ("/coffee-equipment/", "咖啡器具选购指南"),
    "咖啡装备": ("/coffee-equipment/", "咖啡器具选购指南"),
    "咖啡与健康": ("/health/", "咖啡与健康完全指南"),
    "咖啡烘焙": ("/coffee-beans/", "咖啡豆完全指南"),
    # 间接：把没有专属 pillar 的类目归到最相关的 pillar
    "咖啡文化": ("/coffee-beans/", "咖啡豆完全指南"),
    "咖啡品牌与故事": ("/coffee-equipment/", "咖啡器具选购指南"),
    "咖啡旅行": ("/coffee-beans/", "咖啡豆完全指南"),
    "可持续咖啡": ("/coffee-beans/", "咖啡豆完全指南"),
    "咖啡与食物搭配": ("/brewing-methods/", "咖啡冲煮方法完全指南"),
    "咖啡热点分析": ("/", "Coffee Prism 主页 (查看所有最新文章)"),
    "咖啡知识": ("/coffee-beans/", "咖啡豆完全指南"),
    "手冲咖啡": ("/brewing-methods/pour-over-v60/", "V60 手冲咖啡完全指南"),
    # Trending news 文章的兜底（main_topic 字段也用类目名）
    "热点": ("/", "Coffee Prism 主页"),
}


def pillar_link_for_topic(category):
    """Return (url, title) tuple for the pillar matching this category, or None."""
    return PILLAR_BY_CATEGORY.get(category)


def inject_pillar_link(article_content, category):
    """Insert a "完整指南" link to the pillar after the article's H1 line.
    Returns the modified article_content (unchanged if no pillar mapped).
    Idempotent — won't double-inject if the marker is already present."""
    pillar = pillar_link_for_topic(category)
    if not pillar:
        return article_content
    if "📚 想要系统化" in article_content:
        return article_content  # already injected
    url, pname = pillar
    if pname.startswith("Coffee Prism 主页"):
        # For trending, point users to category page rather than vague "homepage"
        block = f"\n\n> 📰 想看更多咖啡行业热点分析？看 [咖啡热点分析](/categories/咖啡热点分析/) — 我们追踪的所有行业新闻和深度解读。\n\n"
    else:
        block = f"\n\n> 📚 想要系统化的纯净版本？看 [{pname}]({url}) — 一篇页面把这个领域的核心知识全串起来。\n\n"

    lines = article_content.split('\n')
    for i, line in enumerate(lines):
        if line.strip().startswith('# ') and not line.strip().startswith('## '):
            head = '\n'.join(lines[:i + 1])
            tail = '\n'.join(lines[i + 1:])
            return head + block + tail
    return block.lstrip() + article_content

# 常见的 AI 腔句式：提示词里禁止，scripts/content_checks.py 会统计密度。
AI_TELLS = "「不是……而是……」「不仅……更……」「值得注意的是」「需要指出的是」「总而言之」「综上所述」「总的来说」「让我们……」「在当今……时代」「说白了」「核心是：」「完美」「终极」「解锁」「密码」「一站式」「赋能」"


def get_system_prompt():
    """系统提示词：事实规则优先。

    旧版要求模型写 3-5 个「有来源的数字」、1-2 段专家引语和中国市场数据，却不给
    任何来源，免费模型只能编造。现在只允许写有把握的通识和常见操作参数；
    统计、价格、研究、引语一律不写（热点文章只能用新闻原文里的事实）。
    """
    today = datetime.date.today()
    return f"今天是 {today.isoformat()}（{today.year} 年）。涉及年份时以此为准，不要写过期年份。\n\n" + f"""你是 Coffee Prism（中文咖啡知识站）的编辑，为在家做咖啡、买咖啡的中文读者写实用、准确的文章。

## 事实规则（最重要，违反会导致文章被丢弃）
- 只写你有把握、业内普遍认可的知识。拿不准的内容宁可不写。
- 禁止编造：统计数字、市场规模、增长率、调查结果、价格、销量、研究结论、论文、机构报告、专家或冠军的语录、具体人名和店铺的经历。
- 不要写「据……报告」「研究表明」「数据显示」「调查发现」「专家指出」这类说法，也不要用 > 引用块引用任何人或机构。
- 操作参数（水温、粉水比、研磨度、萃取时间、克数）可以写，用常见范围表达（如「90–96°C」），并说明这是起点、需要按口味调整。
- 不要声称你或「我们」做过测试、品鉴、拜访，或拥有任何资质。
- 不要写网址，除了下文规定格式的 Amazon 搜索链接。

## 写作风格
- 开门见山：第一段直接回答标题里的问题。
- 用具体做法、判断方法和常见错误代替空泛形容；一段只讲一件事，句子短一些。
- 不要用这些 AI 腔：{AI_TELLS}。
- 不滥用加粗；同一事物始终用同一个名称；不要堆砌关键词。"""


def get_article_prompt(specific_topic, main_topic):
    """生成针对特定主题的文章提示词"""
    year = datetime.date.today().year
    return f"""请为 Coffee Prism 写一篇关于「{specific_topic}」（类目：{main_topic}）的文章。

## 标题
- 15–30 个汉字，包含「{specific_topic}」或它的自然说法，写清楚读者能得到什么。
- 不要用《》，不要用「终极」「完全指南」「深度解析」「解锁」「密码」这类套话。
- 一般不写年份；确有必要时只能写 {year} 年。

## 正文
- 第一段 80–150 字：直接回答读者最想知道的问题，能单独成段被引用。主关键词在第一段出现一次即可，不要加粗。
- 之后按读者真正需要的步骤或问题组织，3–6 个 H2；每个 H2 开头一两句先给结论。需要时再用 H3、列表或表格（表格只放操作参数和对比，不放编造的数据）。
- 至少 1 个 H2 用读者会问的自然问句。不要让每个 H2 都以「{specific_topic}的……」开头。
- 写具体：怎么做、怎么判断做对了、常见错误和怎么调整。
- 如果确实有读者常问的问题，加一个「## 常见问题解答」，3–5 个 H3 问题，每个回答 50–120 字，第一句就是答案。
- 不需要「要点速览」和「总结」章节，不要写总结式结尾。
- 长度跟着内容走：去空白 1500–3000 字，讲清楚就停，不要注水。
- 产品推荐：确有需要时最多 3 个，格式 [产品英文名](https://www.amazon.com/s?k=英文搜索词)，不写价格。
- 面向中国读者：可以提淘宝、京东等购买渠道和人民币，但不写具体价格、销量和市场数据。
- 再次提醒：不写统计、研究、报告、价格、引语和亲身经历；没有把握的句子删掉。

## 输出格式（必须严格遵守，否则文章会被丢弃）

用以下 XML 标记分开输出：

<TITLE>
纯文本标题（不带 # 《》 ** 等符号）
</TITLE>

<DESCRIPTION>
80–140 字纯文本摘要：第一句直接回答标题里的问题；不要 Markdown 符号，不要「本文将」。
</DESCRIPTION>

<BODY>
完整 Markdown 正文，从第一段开始，不要重复标题，不要 front matter 或 ---。
</BODY>

现在请写这篇文章。"""


MIN_BODY_CHARS = 1500


def _strip_thinking(text):
    """Drop <think>...</think> blocks and leading YAML front matter the LLM
    might have hallucinated."""
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL).strip()
    return text


def parse_structured_output(raw):
    """Parse the LLM's <TITLE>/<DESCRIPTION>/<BODY> output.
    Returns (title, description, body); missing parts are None.
    Strips common LLM noise like trailing markdown bullets in title."""
    if not raw:
        return None, None, None
    raw = _strip_thinking(raw)

    title_match = re.search(r'<TITLE>\s*(.*?)\s*</TITLE>', raw, re.DOTALL | re.IGNORECASE)
    desc_match = re.search(r'<DESCRIPTION>\s*(.*?)\s*</DESCRIPTION>', raw, re.DOTALL | re.IGNORECASE)
    # Models sometimes omit </BODY>. Take the rest of the output then, instead of
    # falling back to the raw text, which once published tags and a blockquote as
    # the title (three posts, 2026-05-22 and 2026-11-18).
    body_match = re.search(r'<BODY>\s*(.*?)\s*(?:</BODY>|\Z)', raw, re.DOTALL | re.IGNORECASE)

    desc = None
    if desc_match:
        desc = desc_match.group(1).strip()
        # 保险：剥掉 markdown 痕迹，压成单行纯文本
        desc = re.sub(r'[*_`>#\[\]]', '', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()[:160] or None

    if title_match and body_match:
        title = title_match.group(1).strip()
        body = re.sub(r'</?(?:TITLE|DESCRIPTION|BODY)>', '', body_match.group(1), flags=re.IGNORECASE).strip()
        # Sanitize title: drop H markers, asterisks, book marks, leftover quotes
        title = title.lstrip('#').strip().strip('*').strip()
        title = title.strip('《》').strip('"').strip("'").strip()
        # Drop the "标题：" prefix if LLM still wrote it
        for marker in ("**标题**", "标题：", "标题:", "**标题：**", "**标题:**"):
            if title.startswith(marker):
                title = title[len(marker):].strip()
        return title, desc, body

    # Fallback: no XML markers, treat full output as body and let downstream
    # extract_title heuristic try to recover a title from H1
    return None, desc, raw


def _body_chars(body):
    """Count non-whitespace chars in markdown body."""
    if not body:
        return 0
    return len(re.sub(r'\s+', '', body))


def generate_article(topic_info):
    """生成咖啡文章。返回 'TITLE\\n\\nBODY' 形式的合并文本（保持向后兼容
    save_article 的接口），或 None。

    内含字数重试：第一次输出 < MIN_BODY_CHARS 时再请求一次扩展版。
    """
    main_topic = topic_info["main_topic"]
    specific_topic = topic_info["specific_topic"]
    print(f"正在生成关于「{main_topic}：{specific_topic}」的文章 (模型: {MODEL_NAME})...")

    messages = [
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": get_article_prompt(specific_topic, main_topic)},
    ]

    raw = call_llm(messages)
    if not raw:
        print("❌ API 未返回任何内容")
        return None

    title, desc, body = parse_structured_output(raw)
    char_count = _body_chars(body)
    print(f"  第 1 次：title={'OK' if title else 'MISSING'}, desc={'OK' if desc else 'MISSING'}, body={char_count} 字")

    # Retry once if too short
    if char_count < MIN_BODY_CHARS and body:
        print(f"  ⚠️  正文过短（{char_count} < {MIN_BODY_CHARS}），重试加扩展指令")
        retry_messages = list(messages) + [
            {"role": "assistant", "content": raw},
            {"role": "user", "content": (
                f"上一版正文只有 {char_count} 字（去空白），低于 {MIN_BODY_CHARS} 字。"
                f"请保留已有内容，补充更多具体步骤、判断方法和常见错误及调整办法，"
                f"不要补充统计数字、价格、研究、引语或亲身经历。仍然用 <TITLE></TITLE> + <DESCRIPTION></DESCRIPTION> + <BODY></BODY> 格式输出。"
            )},
        ]
        raw2 = call_llm(retry_messages)
        if raw2:
            t2, d2, b2 = parse_structured_output(raw2)
            cc2 = _body_chars(b2)
            print(f"  第 2 次：title={'OK' if t2 else 'MISSING'}, body={cc2} 字")
            if cc2 > char_count:
                title, desc, body, char_count = (t2 or title), (d2 or desc), b2, cc2

    if not body:
        return None

    # LLM 给的 description 通过 HTML 注释随正文传递（save_article 会取出并
    # 从正文剥掉）——避免为传一个字段改动整条 string 管线。
    if desc:
        body = f"<!-- seo-description: {desc} -->\n\n{body}"

    # Compose into the legacy "# title\n\nbody" form so save_article's existing
    # extract_title path can still find the title (defense in depth).
    if title:
        return f"# {title}\n\n{body}".strip()
    return body

def generate_seo_description(title, specific_topic, article_content):
    """生成SEO优化的meta description。
    优先用 LLM 通过 <DESCRIPTION> 标签给出、随正文传递的注释；
    回退到首段提取（跳过引用/注释/CTA 行，剥掉 markdown 痕迹）。"""
    m = re.search(r'<!--\s*seo-description:\s*(.*?)\s*-->', article_content, re.DOTALL)
    if m:
        desc = re.sub(r'\s+', ' ', m.group(1)).strip()
        if len(desc) >= 50:
            return desc[:160]

    # 回退：从文章第一个"真正文段"提取
    lines = article_content.strip().split('\n')
    first_paragraph = ""

    for line in lines:
        clean_line = line.strip()
        # 跳过标题行、空行、blockquote/CTA 行（'>' 开头）、HTML 注释
        if (clean_line and not clean_line.startswith('#')
                and not clean_line.startswith('>')
                and not clean_line.startswith('<!--')
                and len(clean_line) > 50):
            # 剥 markdown 痕迹：**加粗**、[链接](url)、`code`
            clean_line = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', clean_line)
            clean_line = re.sub(r'[*_`]', '', clean_line)
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
            
        if cleaned_line.startswith(('>', '<')):
            continue  # blockquotes (the injected guide link) and stray tags are never titles

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
            # 必须重置：否则循环结束后的"保存最后一个"会把同一问答再存一次（历史重复 bug）
            current_question = None
            current_answer_lines = []
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

    # 按问题去重 + 截断超长回答（防止总结段落漏进最后一个 FAQ 回答）
    seen = set()
    deduped = []
    for item in faq_items:
        if item["q"] in seen:
            continue
        seen.add(item["q"])
        if len(item["a"]) > 300:
            item = {"q": item["q"], "a": item["a"][:297] + "..."}
        deduped.append(item)

    return deduped[:7]  # 最多7个FAQ


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
        slug = unique_slug(slug, unique_id[:6])
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
        seed_line = f"topic_seed: {yaml_str(topic_info['seed'])}\n" if topic_info.get("seed") else ""
        front_matter = f"""---
title: {yaml_str(title)}
date: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
lastmod: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
draft: false
categories: [{yaml_str(category)}]
tags: {json.dumps(tags, ensure_ascii=False)}
description: {yaml_str(seo_description)}
keywords: {json.dumps(tags[:5], ensure_ascii=False)}
author: "Coffee Prism"
faq: {faq_json}
slug: {yaml_str(slug)}
canonicalURL: "https://www.coffeeprism.com/posts/{slug}/"
topic_keyword: {yaml_str(topic_info['specific_topic'])}
{seed_line}---

"""
        
        # --- UPDATED: Process article content - remove original title line(s) based on index ---
        content_lines = article_content.strip().split('\n')
        # Create the processed content by excluding the title lines
        processed_content_lines = []
        for i, line in enumerate(content_lines):
            if i not in title_line_indices:
                processed_content_lines.append(line)
        
        processed_content = '\n'.join(processed_content_lines).strip()
        # 剥掉 description 传递注释（它只服务 frontmatter，不该出现在正文里）
        processed_content = re.sub(r'<!--\s*seo-description:.*?-->\s*', '', processed_content, flags=re.DOTALL).strip()
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
    
    if char_count < MIN_BODY_CHARS:
        issues.append(f"⚠️  文章过短 ({char_count}字)，低于 {MIN_BODY_CHARS} 字")
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
    
    if keyword_count < 2:
        warnings.append(f"⚡ 关键词只出现 {keyword_count} 次，检查标题和首段是否写到了主题")
    elif keyword_count > 15:
        warnings.append(f"⚡ 关键词可能过多 ({keyword_count}次)，注意避免堆砌")
    else:
        print(f"✅ 关键词频率合理")
    
    # 4. 检查标题结构 (H2, H3)
    h2_count = article_content.count('\n## ')
    h3_count = article_content.count('\n### ')
    print(f"📋 标题结构: {h2_count} 个H2标题, {h3_count} 个H3标题")
    
    if h2_count < 2:
        issues.append(f"⚠️  H2标题过少 ({h2_count}个)")
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
    
    if len(paragraphs) < 5:
        warnings.append(f"⚡ 段落较少 ({len(paragraphs)}个)")
    
    # 7. 检查产品链接
    amazon_links = article_content.count('amazon.com')
    print(f"🔗 Amazon产品链接: {amazon_links} 个")
    
    if amazon_links == 0:
        pass  # 产品链接可有可无，不为凑链接改文章
    elif amazon_links > 3:
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

    print(f"  正在用 {MODEL_NAME} 评估新闻热度...")
    result = call_llm([
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


def news_has_facts(news_item, min_chars=120):
    """True when the news summary carries real content beyond its own headline."""
    summary = re.sub(r"\s+", " ", news_item.get("summary") or "")
    for part in re.split(r"\s+-\s+", news_item.get("title") or ""):
        if part.strip():
            summary = summary.replace(part.strip(), " ")
    return len(re.sub(r"\s+", "", summary)) >= min_chars


def get_trending_article_prompt(news_item):
    """热点文章提示词：事实只能来自新闻条目本身，并链接原文。"""
    return f"""请为 Coffee Prism 写一篇解读下面这条咖啡行业新闻的文章。

## 新闻信息（这是全文唯一的事实来源）
- 标题：{news_item['title']}
- 摘要：{news_item['summary']}
- 原文链接：{news_item['link']}
- 建议角度：{news_item.get('angle', '这件事对普通咖啡消费者意味着什么')}
- 目标关键词：{', '.join(news_item.get('target_keywords', []))}

## 事实规则（违反会导致文章被丢弃）
- 关于这条新闻的事实（数字、日期、公司、人物、表态）只能来自上面的标题和摘要。摘要里没有的，不要补充、推测或编造。
- 正文里不要提「标题」「摘要」这些字眼，也不要讨论新闻没写什么；直接写已知事实，没有的信息就不写。
- 第一次提到这条新闻时，用 Markdown 链接到原文：[新闻来源]({news_item['link']})。不要写其他网址（Amazon 搜索链接除外）。
- 不要写统计表格，不要用 > 引用块，不要虚构任何人的话；需要引用时只能原样引用摘要里的句子并注明来自原文。
- 背景知识只写业内普遍认可的常识，不写市场规模、价格、销量或增长率。
- 分析和判断要明确写成编辑观点（如「我们认为」「可能」），不要写成事实，不要给出带数字的预测。

## 结构
- 标题 15–30 字，准确概括事件，不标题党，不用「震惊」「重磅」。
- 第一段：2–3 句说清发生了什么、为什么值得关注，并链接原文。
- 2–4 个 H2：事件要点（只用新闻里的事实）、相关背景常识、对国内咖啡爱好者的实际影响（可以怎么做、要注意什么）、编辑观点。
- 可选「## 常见问题解答」：2–4 个读者真正会问的问题，回答 50–120 字，第一句就是答案。
- 长度：去空白 1200–2500 字。素材有限就写短，不要注水。
- 产品推荐最多 2 个，格式 [产品英文名](https://www.amazon.com/s?k=英文搜索词)，不写价格，不生硬。

## 输出格式
- 第一行以 `# ` 开头的标题，然后是正文。
- 不要输出 front matter 或 `---`。

现在请写这篇文章。"""


def generate_trending_article(news_item):
    """生成热点分析文章"""
    print(f"\n🔥 正在生成热点分析文章: {news_item['title'][:50]}...")

    messages = [
        {"role": "system", "content": get_system_prompt() + "\n\n本篇是新闻解读：例外地，必须用 Markdown 链接新闻原文一次；关于新闻的事实只能来自给定的标题和摘要。"},
        {"role": "user", "content": get_trending_article_prompt(news_item)}
    ]

    article_content = call_llm(messages)
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

    # 近似重复拦截：同一条行业新闻（如"咖啡价格上涨"）常连续多天出现
    score, near = most_similar_title(title, [p["title"] for p in load_existing_posts()])
    if score >= DUP_TITLE_THRESHOLD:
        print(f"  ❌ 热点文章标题「{title}」与已有「{near}」近似（{score:.2f}），跳过")
        return False

    today = datetime.date.today().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.now().strftime("%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    slug = slugify.slugify(title, separator='-', max_length=50)
    if not slug:
        slug = "trending-analysis"
    filename = f"{today}-{timestamp}-trending-{slug}-{unique_id}.md"
    slug = unique_slug(slug, unique_id[:6])

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
title: {yaml_str(title)}
date: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
lastmod: {today}T{datetime.datetime.now().strftime('%H:%M:%S')}+08:00
draft: false
categories: ["咖啡热点分析"]
tags: {json.dumps(tags, ensure_ascii=False)}
description: {yaml_str(seo_description)}
keywords: {json.dumps(tags[:5], ensure_ascii=False)}
author: "Coffee Prism"
faq: {faq_json}
slug: {yaml_str(slug)}
canonicalURL: "https://www.coffeeprism.com/posts/{slug}/"
trending: true
news_source: {yaml_str(news_item.get('link', ''))}
---

"""

    # 处理正文
    content_lines = article_content.strip().split('\n')
    processed_lines = [line for i, line in enumerate(content_lines) if i not in title_line_indices]
    processed_content = '\n'.join(processed_lines).strip()

    # 给热点文章注入 pillar / 类目链接（导引到「咖啡热点分析」分类页）
    processed_content = inject_pillar_link("\n# placeholder\n\n" + processed_content, "咖啡热点分析")
    # Strip the placeholder header we used to anchor the injection
    processed_content = processed_content.replace("\n# placeholder\n", "", 1).lstrip()

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(front_matter + processed_content)
        print(f"  热点文章已保存至: {filepath}")
        # Inject 相关阅读 内链到这篇 trending 文章
        try:
            inject_related_for_latest(title)
        except Exception as e:
            print(f"  ⚠️  内链注入跳过（非致命）：{e}")
        return True
    except Exception as e:
        print(f"  保存热点文章失败: {e}")
        return False


def _split_generated(article_content):
    """'# 标题\n\n<!-- seo-description: … -->\n\n正文' -> (title, description, body)."""
    m = re.match(r"\s*#\s+(.+?)\n+(?:<!-- seo-description: (.*?) -->\n+)?", article_content, re.S)
    if not m:
        return "", "", article_content
    return m.group(1).strip(), (m.group(2) or "").strip(), article_content[m.end():]


def _join_generated(title, desc, body):
    head = f"# {title}\n\n" + (f"<!-- seo-description: {desc} -->\n\n" if desc else "")
    return head + body.strip()


def _numbers(text):
    return set(re.findall(r"\d+(?:\.\d+)?", text))


def enforce_fact_rules(article_content, allowed_urls=(), source_text="", label=""):
    """Block invented facts (scripts/content_checks.py). One repair round: the model may only
    delete or rephrase the flagged sentences. Returns the article, or None to skip it."""
    title, desc, body = _split_generated(article_content)
    problems = content_checks.findings(title, desc + "\n\n" + body, allowed_urls=allowed_urls, source_text=source_text)
    density = content_checks.ai_tell_density(body)
    if density > 1.0:
        print(f"⚡ {label}AI 腔句式偏多（每千字 {density} 处）")
    if not problems:
        print(f"✅ {label}事实规则检查通过")
        return article_content
    print(f"⚠️  {label}发现 {len(problems)} 处违反事实规则，请模型删改一次：")
    for code, snippet in problems[:12]:
        print(f"   [{code}] {snippet}")
    listing = "\n".join(f"- [{code}] {snippet}" for code, snippet in problems[:12])
    raw = call_llm([
        {"role": "system", "content": get_system_prompt()},
        {"role": "user", "content": (
            "下面这篇文章里有违反事实规则的内容（编造的统计、研究、报告、引语、价格、网址或亲身经历）：\n"
            f"{listing}\n\n"
            "请删除这些句子，或改写成不含这些数字、来源、引语和价格的说法。不要新增任何事实、数字、人名、"
            "机构或网址；其余内容尽量保持原样。按原格式输出：\n"
            f"<TITLE>\n{title}\n</TITLE>\n<DESCRIPTION>\n{desc}\n</DESCRIPTION>\n<BODY>\n{body.strip()}\n</BODY>"
        )},
    ])
    _, new_desc, new_body = parse_structured_output(raw)
    if not new_body or new_body.strip() == (raw or "").strip():
        print(f"❌ {label}删改失败（模型没有按格式返回），跳过本篇")
        return None
    new_desc = new_desc or desc
    remaining = content_checks.findings(title, new_desc + "\n\n" + new_body, allowed_urls=allowed_urls, source_text=source_text)
    added = _numbers(new_desc + new_body) - _numbers(desc + body)
    if remaining or added or len(new_body) < 0.6 * len(body):
        why = [c for c, _ in remaining][:5] or (["新增了数字 " + ", ".join(sorted(added)[:5])] if added else ["删改后篇幅过短"])
        print(f"❌ {label}删改后仍不合格（{'; '.join(why)}），跳过本篇")
        return None
    print(f"✅ {label}删改后通过事实规则检查")
    return _join_generated(title, new_desc, new_body)


def process_and_save_article(article_content, topic, label=""):
    """文章后处理通用流程：硬质量门槛 -> Amazon链接 -> 保存。

    硬质量门槛（不达标的直接跳过，不写入仓库）：
    1. title 必须能从内容里成功提取（不能 fallback 到「默认标题」）
    2. 文章正文字符数（去空白后）必须 >= MIN_CHARS
    3. 标题不能与已发布文章重名（防 keyword 内卷）
    """
    MIN_CHARS = 1500  # 历史问题：80% 文章 < 200 字。强制下限避免再产出薄内容
    title, _ = extract_title(article_content)

    # Gate 1: title 提取失败（含把标签或导读引用块误当标题的情况）
    if (not title or title in ("默认标题", "---") or title.startswith(("#", ">", "<"))
            or "📚" in title or re.search(r"</?(?:TITLE|BODY|DESCRIPTION)>", title, re.IGNORECASE)):
        print(f"❌ {label}标题提取失败（得到 '{title}'），跳过本篇不写入仓库")
        return False

    # Gate 2: 字数下限
    char_count = len(article_content.replace(' ', '').replace('\n', '').replace('\t', ''))
    if char_count < MIN_CHARS:
        print(f"❌ {label}文章过短（{char_count} 字 < {MIN_CHARS}），跳过本篇不写入仓库")
        return False

    # Gate 3: 重名 / 近似重名标题检测（站内已有 500+ 篇存在近似重复，别再加）
    try:
        existing_titles = [p["title"] for p in load_existing_posts()]
        if title in existing_titles:
            print(f"❌ {label}标题「{title}」已存在，跳过避免关键词内卷")
            return False
        score, near = most_similar_title(title, existing_titles)
        if score >= DUP_TITLE_THRESHOLD:
            print(f"❌ {label}标题「{title}」与已有「{near}」近似（{score:.2f}），跳过避免关键词内卷")
            return False
    except Exception as e:
        print(f"⚠️  重名检查跳过（非致命）：{e}")

    article_content = enforce_fact_rules(article_content, label=label)
    if article_content is None:
        return False

    try:
        check_content_quality(article_content, title, topic['specific_topic'])
    except Exception as e:
        print(f"⚠️  质量检查时出错 (非致命): {e}")

    try:
        print("\n🔗 处理Amazon链接...")
        article_content = validate_and_update_amazon_links(article_content)
    except Exception as e:
        print(f"⚠️  验证/更新 Amazon 链接时出错 (非致命): {e}")

    # Inject pillar link at top of body (before saving) — funnels traffic
    article_content = inject_pillar_link(article_content, topic["main_topic"])

    print("\n💾 保存文章...")
    success = save_article(article_content, topic)
    if success:
        print(f"✅ {label}文章生成并保存成功！")
        # Post-save hook: 给新文章注入「相关阅读」内链
        try:
            inject_related_for_latest(title)
        except Exception as e:
            print(f"⚠️  内链注入跳过（非致命）：{e}")
    else:
        print(f"❌ {label}文章保存失败")
    return success


def inject_related_for_latest(title):
    """新文章保存后，从最近写入的几个文件里反查 title，给它跑一遍
    inject_internal_links 注入「相关阅读」区块。"""
    import subprocess
    posts = sorted(Path("content/posts").glob("*.md"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
    for p in posts[:5]:
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(800)
            if f'title: {yaml_str(title)}' in head or f'title: "{title}"' in head:
                result = subprocess.run(
                    ["python3", "scripts/inject_internal_links.py",
                     "--apply", "--files", str(p)],
                    capture_output=True, text=True, timeout=60,
                )
                if "注入/刷新内链：1" in result.stdout:
                    print(f"🔗 已为 {p.name} 注入相关阅读内链")
                return
        except Exception:
            continue


def _count_recent_trending(days=7):
    """计 N 天内已经发布的 trending 文章数。用于限频。"""
    import datetime as _dt
    cutoff = _dt.date.today() - _dt.timedelta(days=days)
    count = 0
    for p in Path("content/posts").glob("*-trending-*.md"):
        try:
            with open(p, encoding="utf-8") as f:
                head = f.read(400)
            dm = re.search(r'^date:\s*(\d{4}-\d{2}-\d{2})', head, re.M)
            if not dm:
                continue
            d = _dt.date.fromisoformat(dm.group(1))
            if d >= cutoff:
                count += 1
        except Exception:
            continue
    return count


TRENDING_QUOTA_DAYS = 7
TRENDING_QUOTA = int(os.getenv("TRENDING_QUOTA") or 2)  # 7 天内最多 N 篇热点分析
REGULAR_ARTICLES_PER_RUN = int(os.getenv("REGULAR_ARTICLES_PER_RUN") or 3)


def main():
    print("开始自动文章生成流程...")
    print(f"🤖 LLM providers: {describe_providers()}")
    if not PROVIDERS:
        return 2

    random.seed(time.time())
    articles_saved = 0

    # ========== 第一阶段：热点新闻分析（带配额）==========
    print("\n" + "=" * 60)
    print("=== 第一阶段：热点新闻抓取与分析 ===")
    print("=" * 60)

    recent_trending = _count_recent_trending(days=TRENDING_QUOTA_DAYS)
    print(f"📊 最近 {TRENDING_QUOTA_DAYS} 天 trending 文章数: {recent_trending} / 配额 {TRENDING_QUOTA}")

    if recent_trending >= TRENDING_QUOTA:
        print(f"🚫 已达 trending 配额，跳过热点分析（保持主题多样性）")
    else:
        try:
            news_items = fetch_coffee_news()
            trending = evaluate_news_worthiness(news_items)
            if trending and not news_has_facts(trending):
                # Google News RSS 的「摘要」通常只是标题加媒体名。只能用新闻原文事实的规则下，
                # 只有标题写不出有内容的文章，旧版就是在这里编造了数据表和引语。
                print(f"\n📋 热点「{trending['title'][:40]}」只有标题、没有可用的事实，跳过热点文章")
                trending = None
            if trending:
                print(f"\n🔥 发现值得分析的热点: {trending['title'][:60]}")
                trending_content = generate_trending_article(trending)
                if trending_content:
                    trending_content = enforce_fact_rules(
                        trending_content,
                        allowed_urls=[trending["link"]],
                        source_text=f"{trending['title']}\n{trending.get('summary', '')}",
                        label="热点文章：",
                    )
                if trending_content:
                    try:
                        trending_content = validate_and_update_amazon_links(trending_content)
                    except Exception as e:
                        print(f"⚠️  处理热点文章链接时出错 (非致命): {e}")
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

    # ========== 第二阶段：常规主题文章（数量↑、平衡选题） ==========
    print("\n" + "=" * 60)
    print(f"=== 第二阶段：常规主题文章生成（目标 {REGULAR_ARTICLES_PER_RUN} 篇）===")
    print("=" * 60)

    existing_posts = load_existing_posts()
    seeds = select_random_coffee_topics(REGULAR_ARTICLES_PER_RUN, existing_posts)

    for i, seed in enumerate(seeds, 1):
        print(f"\n{'='*60}")
        print(f"--- 生成第 {i} 篇常规文章 ---")
        print(f"种子: {seed['main_topic']} - {seed['specific_topic']}（已有近似文章 {seed['seed_coverage']} 篇）")
        print(f"{'='*60}")

        if all(p["dead"] for p in PROVIDERS):
            print("❌ 所有 LLM provider 均不可用，停止生成")
            break

        topic = plan_fresh_topic(seed, existing_posts)
        if not topic:
            continue
        article_content = generate_article(topic)
        if not article_content:
            print(f"❌ 无法生成关于「{topic['main_topic']}：{topic['specific_topic']}」的文章，跳过")
            continue

        print(f"\n✅ 文章生成成功！开始后处理...")
        if process_and_save_article(article_content, topic, label=f"第{i}篇"):
            articles_saved += 1
            # 让同一次运行里的后续选题也能看到这篇（防止同批次撞题）
            existing_posts = load_existing_posts()

    print(f"\n{'='*60}")
    print(f"自动文章生成完成！共保存 {articles_saved} 篇文章。")
    print(f"{'='*60}")

    if articles_saved == 0:
        # 非 0 退出码 → Actions 标红并邮件通知，不再"绿灯但 0 产出"
        print("::error title=未生成任何文章::请检查上方日志：LLM provider 不可用（key 失效 / 余额不足 / 服务不可达），或选题全部与已有文章重复、未通过质量门槛")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())