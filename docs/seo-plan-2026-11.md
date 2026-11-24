# Coffee Prism 搜索与变现计划（2026-11-24 起）

站长 2026-11-24 批准整体方案（"所有的都按照你的想法来吧"）。本文记录数据、调研结论、行动和衡量方式，后续每次检查都在这里更新。

## 现状（数据截至 2026-11-23）

**Bing 是唯一有流量的搜索渠道**
- 近 30 天：289 次点击、1.57 万次展示，比前 30 天少 24%；从 11 月 9 日那周起，每天展示从约 800 次降到约 400 次。
- 近 3 个月：1,200 次点击、6.2 万次展示。主要关键词：

| 关键词 | 展示 | 平均排名 | 点击率 |
|---|---:|---:|---:|
| 咖啡豆 | 9,100 | 6.5 | 0.47% |
| 摩卡壶 | 2,500 | 5.2 | 0.87% |
| 蓝山咖啡 | 2,200 | 3.8 | 2.02% |
| 法压壶 | 1,700 | 5.8 | 1.71% |
| 冷咖啡 | 1,300 | 5.1 | 0.38% |
| 意式浓缩 | 1,300 | 6.2 | 0.39% |
| 咖啡冲泡 | 1,300 | 3.0 | 0%（0 次点击） |
| coffee brewing methods | 1,200 | 5.6 | 0.25% |

- 抓取正常（Site Explorer）：925 页已收录，0 个错误，最近抓取在 11 月 18–20 日。全站只有 1 个外链。

**Copilot（Bing 的 AI 回答）**
- 3 个月引用 6.93 万次，约 58% 落在 8 个指南页上（冲泡方法 1.51 万、咖啡豆 0.9 万、意式 0.5 万、冷萃 0.49 万、摩卡壶 0.41 万……）。
- Copilot 不在中国大陆提供服务，所以这些引用主要来自大陆以外的读者。

**其他渠道和统计**
- Google 收录了 546 页，但 0 次点击，平均排名 51。这个中文站在 Google 上没有机会，不投入。
- GA4 统计不到大陆访客：它的数据上报地址在大陆被屏蔽，GA 里看到的大部分是机器人。看真实访问要用 Bing 后台和 Cloudflare 的统计。

**变现**
- 亚马逊：3,014 个联盟链接，全是 amazon.com 搜索链接，其中一半用的是中文关键词，amazon.com 搜中文基本搜不到要的东西。从大陆访问 amazon.com 不稳定，所以这部分收入预期本来就低。
- AdSense：2026 年 9–11 月的测试显示，广告域名在大陆大多能加载。

## 调研结论（2026-11-23/24，详见文末来源）

1. **Copilot 偏爱的页面**：事实清楚、标了来源、开头先给答案、有表格、更新日期可见。实测 schema 和 llms.txt 对引用没有可测的提升。
2. **合并重复文章前先查引用**。有网站删文后 AI 曝光掉了 62%。合并要用 301 或 canonical，把被引用的事实搬进保留的那一篇。
3. **Bing 的 2026 新版指南**点名"无人监督的大规模生成内容"。这就是生成器只发经过检查的少量文章的原因。
4. **11 月的下滑**：Bing 11 月没有排名更新。"咖啡豆"只占 3 个月展示量的 15%，下滑分布在多个词上，主要是 /coffee-beans/（排名 6 → 7）和"咖啡豆种类"分类页（展示减半）。
5. **亚马逊规则**：
   - 不能用脚本抓 amazon.com 来检查链接。
   - 搜索链接和商品链接的佣金一样；厨房用品 4.5%，咖啡豆属于食品杂货，只有 1%，所以器具链接更值钱。
   - 网站上必须有原句 "As an Amazon Associate I earn from qualifying purchases."
   - FTC 要求在链接之前、用正文的语言披露。
6. **中文搜索引擎**：
   - 百度用户最多，但对境外、无备案的新站收录慢、排名吃亏。
   - 头条（豆包的数据来源）、360、搜狗可以低成本试一下。
   - 都需要站长用手机号注册账号。
   - 已测：GitHub Pages 不按 User-Agent 拦截百度爬虫（返回 200）。

## 行动清单

| # | 行动 | 谁 | 状态 |
|---|---|---|---|
| 1 | 修亚马逊链接，见下方说明 | Claude | ✅ 2026-11-24（PR #7） |
| 2 | 联盟披露：页脚加亚马逊要求的英文原句；含亚马逊链接的文章和指南页，在正文前加一行中文披露 | Claude | ✅ 2026-11-24（PR #7） |
| 3 | 生成器：每天 1 篇（原来 3 篇）；选题加"意图"去重；选题时给模型看本类目最近 300 个标题（原来 120 个） | Claude | ✅ 2026-11-24（PR #7） |
| 4 | 重写 8 个指南页，见下方说明。指南页标题下已显示更新日期，并输出带 dateModified 的 Article 结构化数据 | Claude | /coffee-beans/ ✅ 2026-11-24（15 个来源、6 张表）；下一个：冲泡方法总览 |
| 5 | 标题和描述改点击率："咖啡豆"（9,100 次展示，点击率 0.47%）、"咖啡冲泡"（排名 3，0 次点击）、"冷咖啡""意式浓缩"等。每次改动后 2–4 周看 Bing 点击率 | Claude | 随第 4 项 |
| 6 | 被 Copilot 引用最多的文章，按 article-review 技能逐篇修订（阿拉比卡与罗布斯塔 2aeef5a9 等）。同主题重复文章合并进去（Hugo aliases 跳转），合并前先看 Bing 点击和 Copilot 引用 | Claude | 第 4 项之后 |
| 7 | 删掉挂在具体人名下、没有来源的引语 | Claude | ✅ 2026-11-24：78 篇里的 92 条（`scripts/remove_named_quotes.py`） |
| 8 | 下线 Bing 0 点击、0 引用、且编造内容多的旧文：改成草稿，旧网址跳到相关指南页 | Claude | 第 6 项期间 |
| 9 | 百度搜索资源平台：注册、验证（用 HTML 标签或 CNAME）、跑抓取诊断，然后推送 8 个指南页。头条站长平台、360、搜狗同理 | 站长（需要手机号） | 可选 |
| 10 | AdSense：在国家报表里看中国大陆有没有展示和收入；广告位预留高度，避免页面跳动 | 站长看报表；Claude 改样式 | 待办 |
| 11 | IndexNow：改成和上线前的 sitemap 对比，只推真正变化的网址，并把跳转和删除的网址也推一次（原来推 lastmod 在 3 天内的网址，同一网址会连推 3 次） | Claude | ✅ 2026-11-24 |
| 12 | 外链：把指南页里有原创价值的内容（冲泡参数对照表、咖啡因数据）发到知乎、少数派、V2EX 等，附原文链接 | 站长发布，Claude 写稿 | 以后 |

**第 1 项说明（亚马逊链接）**
- 1,504 个中文关键词链接：1,435 个换成英文搜索词（映射表在 `scripts/amazon_query_map.tsv`，经人工抽查）；另外 69 个不是商品、或者链接文字只是"购买链接"这类的，直接去掉链接。
- amazon.cn 和 amazon.co.jp 的链接改成 amazon.com。
- 补上缺失的 tag。
- 渲染时如果发现漏了 tag，自动补上。
- `content_checks` 会拦住新文章里的中文关键词亚马逊链接。

**第 4 项说明（8 个指南页）**
- 写法：开头先给答案，H2 写成读者会问的问题，用表格；每个数字都标来源，删掉没有来源的价格和统计；中文名和原名统一写（如"耶加雪菲 Yirgacheffe"）；页面上显示更新日期。
- 每页改完推一次 IndexNow。
- 顺序：咖啡豆 → 冲泡方法总览 → 意式 → 冷萃 → 摩卡壶 → 法压壶 → 爱乐压 → V60 → 健康，最后是 3 个英文页。

## 不做的事

- 不批量生成、不发没过 `content_checks` 的文章。
- 没有真实改动不动 lastmod。
- 不用脚本访问 amazon.com。
- 不买链接。
- 不在 Google 上花力气。

## 衡量

- **每两周看 Bing**：
  - 点击、展示和点击率，看 8 个指南页和上面表里的关键词；
  - Copilot 引用总数，以及每个指南页的引用。
- **每月看收入**：亚马逊（点击、订单）和 AdSense（展示、每千次展示收入、国家）。
- **检查点**：2026-12-15、2027-01-15。如果 /coffee-beans/ 改完 4 周后点击率没有提升，就换一个标题方向。

## 来源

- Bing：AI Performance 报告 <https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview>
- Bing：索引如何支持 AI 回答 <https://blogs.bing.com/search/May-2026/Evolving-role-of-the-index-From-ranking-pages-to-supporting-answers>
- Bing：重复内容与 AI 搜索 <https://blogs.bing.com/webmaster/2025/12/Does-Duplicate-Content-Hurt-SEO-and-AI-Search-Visibility/>
- Bing 新版站长指南（2026-02） <https://www.searchenginejournal.com/bing-adds-geo-to-official-guidelines-expands-ai-abuse-definitions/568442/>
- 删文导致 AI 曝光下降的案例 <https://searchengineland.com/deleting-blog-posts-hurt-ai-visibility-organic-clicks-502405>
- Copilot 在中国大陆不可用 <https://support.microsoft.com/en-us/topic/26de43a1-c176-4908-bef7-29c8c37ac7ce>
- 亚马逊联盟政策（2026-04-14 生效的修改） <https://affiliate-program.amazon.com/help/operating/policies>
- 亚马逊联盟运营协议 <https://affiliate-program.amazon.com/help/operating/agreement>
- 亚马逊佣金费率 <https://affiliate-program.amazon.com/help/node/topic/GRXPHT8U84RAYDXZ>
- FTC 关于推广披露的问答 <https://www.ftc.gov/business-guidance/resources/ftcs-endorsement-guides-what-people-are-asking>
- GreatFire：Google Analytics 在大陆的可达性 <https://en.greatfire.org/www.google-analytics.com>
- GreatFire：AdSense 广告域名在大陆的可达性 <https://en.greatfire.org/https/pagead2.googlesyndication.com>
- StatCounter：中国搜索引擎份额 <https://gs.statcounter.com/search-engine-market-share/all/china>
