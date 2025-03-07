# Coffee Prism

[![Jekyll site CI](https://github.com/your-username/coffeeprism/workflows/Jekyll%20site%20CI/badge.svg)](https://github.com/your-username/coffeeprism/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Coffee Prism 是一个专注于咖啡知识和产品推荐的网站，基于 Jekyll 构建。  
Coffee Prism is a website focused on coffee knowledge and product recommendations, built with Jekyll.

🌐 **Website**: [https://coffeeprism.com](https://coffeeprism.com)

## 🔍 网站结构 (Website Structure)

网站主要包含以下几个部分：

- **博客文章**：存放在 `_posts` 目录中
- **咖啡专题**：存放在 `collections/_coffee` 目录中
- **咖啡设备**：存放在 `collections/_equipment` 目录中
- **产品数据**：存放在 `_data/products.yml` 文件中
- **页面模板**：存放在 `_layouts` 目录中
- **页面组件**：存放在 `_includes` 目录中
- **样式文件**：存放在 `assets/css` 目录中
- **图片资源**：存放在 `assets/images` 目录中

## 📦 GitHub Actions 规则

本项目使用 GitHub Actions 自动构建和部署网站。遵循以下规则确保顺利发布：

> **重要规则**: 每次推送代码后，务必检查 GitHub Actions 构建是否成功。如发现构建失败，请查看错误日志并修复问题。

### 检查构建状态流程：

1. 推送更改到 GitHub 仓库
2. 前往 [Actions 页面](https://github.com/CoffeePrism/coffeeprism.github.io/actions) 查看构建状态
3. 如果构建失败：
   - 点击失败的工作流程查看详细日志
   - 识别错误原因（通常是 Liquid 模板错误、依赖问题或 YAML 前置格式错误）
   - 本地修复问题并推送更改
   - 重复以上步骤直到构建成功

更多详细信息请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 中的 GitHub Actions 工作流程部分。

## 🚀 如何添加新内容 (How to Add New Content)

### 添加博客文章

1. 在 `_posts` 目录中创建一个新的 Markdown 文件，文件名格式为 `YYYY-MM-DD-title.md`
2. 在文件开头添加 YAML 头信息，例如：

```yaml
---
layout: post
title: "文章标题"
date: YYYY-MM-DD
author: 作者名
categories: [分类1, 分类2]
tags: [标签1, 标签2, 标签3]
featured: true/false
featured_image: /assets/images/image-name.jpg
excerpt: "文章摘要"
---
```

3. 在 YAML 头信息后面添加文章内容，使用 Markdown 格式

### 添加咖啡专题

1. 在 `collections/_coffee` 目录中创建一个新的 Markdown 文件
2. 在文件开头添加 YAML 头信息，例如：

```yaml
---
layout: coffee
title: "咖啡名称"
origin: "产地"
roast_level: "烘焙度"
flavor_profile: ["风味1", "风味2", "风味3"]
tags: [标签1, 标签2, 标签3]
featured_image: /assets/images/image-name.jpg
excerpt: "简短描述"
---
```

3. 在 YAML 头信息后面添加内容，使用 Markdown 格式

### 添加咖啡设备

1. 在 `collections/_equipment` 目录中创建一个新的 Markdown 文件
2. 在文件开头添加 YAML 头信息，例如：

```yaml
---
layout: equipment
title: "设备名称"
brand: "品牌"
type: "设备类型"
price_range: "价格范围"
tags: [标签1, 标签2, 标签3]
featured_image: /assets/images/image-name.jpg
excerpt: "简短描述"
pros_cons:
  pros:
    - "优点1"
    - "优点2"
    - "优点3"
  cons:
    - "缺点1"
    - "缺点2"
    - "缺点3"
---
```

3. 在 YAML 头信息后面添加内容，使用 Markdown 格式

### 添加产品推荐

1. 打开 `_data/products.yml` 文件
2. 在相应的产品类别下添加新产品，例如：

```yaml
coffee_beans:
  - name: "产品名称"
    description: "产品描述"
    image: "/assets/images/products/image-name.jpg"
    price: "价格"
    amazon_id: "亚马逊产品ID"
```

3. 确保 `amazon_id` 是正确的亚马逊产品 ID，这将用于生成亚马逊联盟链接

## 💻 本地开发 (Local Development)

要在本地运行网站进行开发和测试，请按照以下步骤操作：

1. 确保已安装 Ruby 和 Bundler
2. 克隆仓库到本地
3. 在项目根目录运行 `bundle install` 安装依赖
4. 运行 `bundle exec jekyll serve` 启动本地服务器
5. 在浏览器中访问 `http://localhost:4000` 查看网站

## 🌐 部署 (Deployment)

将更改推送到主分支后，网站将自动构建和部署。

## 🖼️ 图片优化 (Image Optimization)

为了提高网站性能，请确保上传的图片已经过优化：

1. 图片尺寸应适合其在网站上的显示大小
2. 使用适当的压缩工具减小文件大小
3. 为产品图片使用统一的尺寸比例（建议 1:1 或 4:3）

## 🤝 贡献指南 (Contributing Guidelines)

We welcome contributions to improve Coffee Prism! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add some amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. Submit a **Pull Request**

Please make sure your code follows our style guide and passes all tests.

## 📝 问题反馈 (Issue Reporting)

If you find a bug or have a feature request, please create an issue using our issue template.

## 📊 项目状态 (Project Status)

此项目处于积极开发和维护中。
This project is actively maintained and under development.

## 📜 许可证 (License)

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
