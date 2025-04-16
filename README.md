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
- **主题**: [PaperMod](https://github.com/adityatelange/hugo-PaperMod)
- **托管**: [GitHub Pages](https://pages.github.com/)
- **自动化内容生成**: OpenAI API + NewsAPI
- **工作流自动化**: GitHub Actions

## 本地开发

要在本地设置和开发 Coffee Prism 网站，请按照以下步骤操作：

### 前提条件

- [Git](https://git-scm.com/)
- [Hugo Extended](https://gohugo.io/installation/) (最新版)
- [Python](https://www.python.org/downloads/) 3.8+

### 安装步骤

1. 克隆仓库
   ```bash
   git clone https://github.com/CoffeePrism/coffeeprism.github.io.git
   cd coffeeprism.github.io
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

Coffee Prism 利用 OpenAI API 和 NewsAPI 自动生成咖啡相关文章:

1. 脚本 `scripts/generate_and_publish.py` 从 NewsAPI 获取最新咖啡新闻
2. 使用 OpenAI API 基于这些新闻生成原创文章
3. 自动添加亚马逊推广链接 (跟踪 ID: coffeeprism-20)
4. 生成的文章自动发布到网站

通过 GitHub Actions 工作流 `.github/workflows/publish.yml` 实现每日自动运行。

要手动运行内容生成:

```bash
# 设置必要的环境变量
export OPENAI_API_KEY="your-openai-api-key"
export NEWSAPI_KEY="your-newsapi-key"

# 运行生成脚本
python scripts/generate_and_publish.py
```

## 贡献指南

我们欢迎社区贡献! 请参阅 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与该项目。

## 许可证

本项目内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。
代码部分采用 [MIT 许可证](LICENSE)。

newsapi: 8e8f884ce8274f698b09aa3f11992b6f