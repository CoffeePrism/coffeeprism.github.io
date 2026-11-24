"""Deterministic checks that keep invented facts out of auto-published articles.

The generator used to ask a free model for statistics, expert quotes and market
data without giving it any sources, so it invented them ("2023年《食品科学》研究显示",
"复旦大学2022年研究", "缓解75%女性的偏头痛"). The prompt no longer asks for any of that;
these checks catch what still slips through. `blocking(...)` findings stop a post
from being published (the generator first asks the model to delete the sentences);
`warnings(...)` are only logged.

Rules adapted from the 2026-11 review of writing-quality skills (Humanizer-zh,
human-writing, claude-blog) and Wikipedia's "Signs of AI writing". Patterns were
written for this site rather than copied.
"""
import datetime
import re
import urllib.parse

# Sentences that attribute a claim to research, data or experts.
ATTRIBUTION = re.compile(
    r"(?:研究|调查|数据|报告|统计|实验|专家|学者|业内人士|权威机构|文献)(?:结果)?(?:表明|显示|发现|指出|认为|证实|称)"
    r"|(?<!依)据[^，。；\n]{0,24}(?:统计|报道|调查|报告|研究|数据|标准|指南|测算)"
    r"|《[^》]{1,30}》[^，。；\n]{0,12}(?:研究|报告|显示|指出|数据)"
    r"|according to|studies? (?:show|suggest|found)|research (?:shows|indicates|found)|survey (?:found|shows)",
    re.I,
)
FIRST_HAND = re.compile(r"我们(?:亲自)?(?:实测|测试|测评|试喝|走访|拜访)|我(?:亲自)?(?:实测|测试|试喝|在店里)|笔者|作为一名[^，。\n]{0,10}(?:咖啡师|烘焙师|专家)|多年(?:从业|经验)的我")
RESIDUE = re.compile(r"<think>|作为(?:一个)?(?:AI|人工智能)|as an AI|希望(?:这篇|本文|以上)[^。\n]{0,8}(?:对你|能)有(?:所)?帮助|如果你(?:还)?有(?:任何)?(?:问题|疑问)|\[(?:插入|INSERT|TODO|TBD)|待核实|NEEDS SOURCE|20[xX]{2}", re.I)
PRICE = re.compile(r"(?:[¥￥$]\s?\d)|\d+(?:\.\d+)?\s*(?:元|美元|块钱)(?![素宝])")
# Percentages, multipliers and big counts outside brewing parameters.
STAT = re.compile(r"\d+(?:\.\d+)?\s*(?:[%％]|倍)|\d+(?:\.\d+)?\s*(?:万|亿)(?:人|家|杯|吨|元|美元|包|袋|次|名|个|位|户|店)?")
BREWING_CONTEXT = re.compile(r"萃取|TDS|浓度|含水|湿度|失重|粉水比|水粉比|研磨|烘焙度|密度|脂肪|乳脂|酒精|可可")
AMAZON_SEARCH = re.compile(r"^https://(?:www\.)?amazon\.com/s\?k=")
OWN_SITE = re.compile(r"^https?://(?:www\.)?coffeeprism\.com/")
CJK = re.compile(r"[\u3000-\u9fff\uff00-\uffef]")
LINK = re.compile(r"\]\((https?://[^)\s]+)\)|(?<![(\w])(https?://[^\s)<>\"'，。]+)")
YEAR = re.compile(r"(?<!\d)(19|20)\d{2}(?!\d)")
GUIDE_QUOTE = re.compile(r"^\s*>\s*(?:📚|📰|☕|📌)")

# Common tells of machine-written Chinese (warning only; density per 1,000 characters).
AI_TELLS = re.compile(
    r"(?:并)?不是[^。！？\n]{0,40}而是|不(?:仅仅|仅|只|单)是[^。！？\n]{0,40}(?:而是|更是)"
    r"|值得注意的是|需要指出的是|总而言之|综上所述|总的来说|让我们[^。！？\n]{0,30}吧"
    r"|在(?:当今|如今|当下|这个)[^，。！？\n]{0,16}(?:时代|社会|世界|背景下)"
    r"|说白了|(?:核心|关键|本质|答案|秘诀)(?:就)?(?:是|在于)?[:：](?!\s*\d)|赋能|一站式|底层逻辑|未来可期|拭目以待"
)


def _sentences(body):
    for line in body.split("\n"):
        if GUIDE_QUOTE.match(line):
            continue  # the site's own guide and e-book links, added by scripts
        # ASCII ?!; end a sentence only before whitespace, so "?k=" inside a URL
        # does not split a link and turn "%E5%92" into a fake percentage.
        for sentence in re.split(r"(?<=[。！？；])|(?<=[!?;])(?=\s|$)", line):
            if sentence.strip():
                yield sentence.strip()


def _strip_code(body):
    return re.sub(r"```.*?```", "", body, flags=re.S)


def findings(title, body, *, allowed_urls=(), source_text="", today=None):
    """Return a list of (code, snippet) pairs that should block publication.

    allowed_urls: external links the article may contain (e.g. the news source).
    source_text: text the article may take facts from (e.g. the news title and summary);
    numbers, prices and years found there are allowed.
    """
    today = today or datetime.date.today()
    text = _strip_code(body)
    found = []
    allowed = set(allowed_urls)
    source_numbers = set(re.findall(r"\d+(?:\.\d+)?", source_text or ""))

    for sentence in _sentences(text):
        has_link = "](" in sentence
        # Link targets are not prose: "%20" in a URL is not a percentage.
        prose = re.sub(r"\]\([^)]*\)|https?://\S+", "]", sentence)
        if ATTRIBUTION.search(sentence) and not has_link:
            found.append(("unsourced-attribution", sentence[:80]))
        if FIRST_HAND.search(sentence):
            found.append(("first-hand-claim", sentence[:80]))
        for m in PRICE.finditer(prose):
            if not set(re.findall(r"\d+(?:\.\d+)?", m.group(0))) <= source_numbers:
                found.append(("price", sentence[:80]))
                break
        for m in STAT.finditer(prose):
            number = re.match(r"\d+(?:\.\d+)?", m.group(0)).group(0)
            if number in source_numbers or BREWING_CONTEXT.search(prose):
                continue
            found.append(("statistic", sentence[:80]))
            break

    for line in text.split("\n"):
        if line.lstrip().startswith(">") and not GUIDE_QUOTE.match(line):
            found.append(("quote-block", line.strip()[:80]))

    for m in LINK.finditer(text):
        url = m.group(1) or m.group(2)
        if not (AMAZON_SEARCH.match(url) or OWN_SITE.match(url) or url in allowed):
            found.append(("external-link", url[:80]))
        elif AMAZON_SEARCH.match(url) and CJK.search(urllib.parse.unquote_plus(url)):
            # amazon.com search returns poor results for Chinese keywords.
            found.append(("amazon-chinese-query", url[:80]))

    for m in YEAR.finditer(title + "\n" + text):
        if int(m.group(0)) > today.year:
            found.append(("future-year", m.group(0)))
    for m in YEAR.finditer(title):
        if int(m.group(0)) != today.year:
            found.append(("title-year", m.group(0)))

    for m in RESIDUE.finditer(text):
        found.append(("residue", m.group(0)[:40]))
    return found


def ai_tell_density(body):
    """AI-tell matches per 1,000 Chinese characters (warning signal only)."""
    chars = len(re.findall(r"[一-鿿]", body)) or 1
    return round(len(AI_TELLS.findall(body)) * 1000 / chars, 2)
