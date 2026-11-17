# Coffee Prism 咖啡棱镜

![Coffee Prism](https://via.placeholder.com/800x400?text=Coffee+Prism)

Coffee Prism（咖啡棱镜）是一个专注于咖啡文化、知识和产品的专业网站。通过丰富的内容和深入的分析，我们帮助咖啡爱好者探索咖啡的多个层面，就像棱镜分解光线一样，展现咖啡的丰富性和复杂性。

网站: [https://www.coffeeprism.com](https://www.coffeeprism.com)

## 内容板块

Coffee Prism 主要包含以下内容板块：

1. **咖啡豆种类**：详细介绍不同产区、不同处理方式的咖啡豆特点
2. **咖啡冲泡方式**：各种冲泡方法的详细步骤和技巧
3. **咖啡产品评测**：专业评测各类咖啡设备和产品
4. **咖啡知识**：分享咖啡相关的专业知识和最新趋势

## 技术架构

本网站基于以下技术构建：

- **静态网站生成器**: [Hugo](https://gohugo.io/)
- **主题**: 基于PaperMod的定制主题
- **自动化内容生成**: OpenAI 兼容 LLM 接口（OpenRouter 等）+ Google News RSS
- **工作流自动化**: 自定义工作流脚本

## 本地开发

要在本地设置和开发 Coffee Prism 网站，请按照以下步骤操作：

### 前提条件

- [Git](https://git-scm.com/)
- [Hugo Extended](https://gohugo.io/installation/) (最新版)
- [Python](https://www.python.org/downloads/) 3.8+

### 安装步骤

1. 克隆源代码仓库
   ```bash
   git clone <源代码仓库URL>
   cd coffeeprism
   ```

2. 初始化子模块 (获取 Hugo 主题)
   ```bash
   git submodule update --init --recursive
   ```

3. 安装 Python 依赖
   ```bash
   pip install requests python-slugify
   ```

4. 本地运行 Hugo 服务器
   ```bash
   hugo server -D
   ```

5. 在浏览器中访问 `http://localhost:1313` 查看网站

### 创建新内容

创建新文章:
```bash
hugo new content posts/my-new-post.md
```

创建新的咖啡豆介绍:
```bash
hugo new content coffee-beans/bean-name.md
```

创建新的冲泡方法介绍:
```bash
hugo new content brewing-methods/method-name.md
```

## 自动内容生成

`.github/workflows/auto_publish.yml` 每天 18:00 UTC 运行 `scripts/generate_and_publish.py`：

1. 从 Google News RSS 抓咖啡新闻，LLM 判断是否值得写热点分析（7 天最多 `TRENDING_QUOTA` 篇，默认 2）
2. 选 `REGULAR_ARTICLES_PER_RUN`（默认 3）个类目「种子」，LLM 在种子下提出站内还没写过的长尾选题，
   与全部已有标题做相似度去重后再写文章（近似重复标题、slug 撞车都会被拦截）
3. 质量门槛（XML 结构化输出 / 字数 / 重名）→ Amazon 联盟链接 → pillar 内链 → 保存到 `content/posts/`
4. Hugo 构建 → 只把 `content/` 提交回 main → 部署 GitHub Pages → IndexNow 推送
5. **一篇都没生成时，运行会被标红并邮件通知**（网站本身照常构建部署）

### LLM 配置（仓库 Settings → Secrets and variables → Actions）

按顺序回退，未配置的自动跳过：

| 顺序 | Secret | 可选 Variable（模型） | 默认模型 |
|---|---|---|---|
| 1 | `LLM_API_KEY` + Variable `LLM_BASE_URL`（任意 OpenAI 兼容接口） | `LLM_MODEL` | `openai/gpt-5.4` |
| 2 | `OPENROUTER_API_KEY` | `OPENROUTER_MODEL` | `openai/gpt-5.4` |
| 3 | `NVIDIA_API_KEY` | `NVIDIA_MODEL` | `z-ai/glm-5.3-flash` |

模型 Variable 可写多个（逗号分隔），按顺序回退；401/403 跳过整个 key，402/404 只跳过当前模型。
当前生产配置（2026-11-17 实测选定的 OpenRouter 免费模型，免费额度：充值 <$10 的账户 50 次/天）：
`OPENROUTER_MODEL=baidu/ernie-5.5-flash-preview:free,nvidia/nemotron-3-ultra-550b-a55b:free`

其他 Variables：`REGULAR_ARTICLES_PER_RUN`、`TRENDING_QUOTA`。手动触发时可在 Actions 页面选择篇数，
或取消「生成新文章」只做构建部署（改了模板/配置时用）。

本地运行：

```bash
pip install -r requirements.txt
export OPENROUTER_API_KEY="sk-or-..."   # 或 LLM_API_KEY + LLM_BASE_URL
python scripts/generate_and_publish.py
```

## 关联项目

🔗 **[FindPicked.com](https://findpicked.com)** — 我们的合作站点，提供 60+ 免费在线工具：
- [AI工具集合](https://findpicked.com/tools/) — 24个AI驱动的免费工具
- [开发者工具](https://findpicked.com/webtools/) — 38个前端在线工具
- [产品评测对比](https://findpicked.com/picks/) — 独立产品评测
- [MCP服务器目录](https://findpicked.com/mcp/) — 70+ 精选MCP服务器
- [Claude技能目录](https://findpicked.com/skill/) — 60+ 精选Claude Code技能

## 贡献指南

我们欢迎社区贡献! 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与该项目。

## 许可证

本项目内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。
代码部分采用 [MIT 许可证](LICENSE)。
