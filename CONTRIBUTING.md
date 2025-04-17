# 贡献指南

感谢您对 Coffee Prism 项目的兴趣！我们欢迎各种形式的贡献，包括内容创作、代码改进、bug修复和功能建议。

## 如何贡献

### 内容贡献

如果您是咖啡领域的专家或爱好者，并希望为网站贡献内容：

1. 您可以通过电子邮件将您的内容发送至 submit@coffeeprism.com

内容贡献可以包括：
- 咖啡豆评测
- 冲泡方法指南
- 咖啡装备评测
- 咖啡知识文章

#### 内容格式要求

所有内容应使用Markdown格式，并包含适当的Front Matter：

```markdown
---
title: "文章标题"
date: YYYY-MM-DD
draft: false
categories: ["分类1", "分类2"]
tags: ["标签1", "标签2"]
---

正文内容...
```

### 代码贡献

如果您想要为网站的代码或自动化流程做出贡献，请通过电子邮件联系我们：dev@coffeeprism.com

## 开发指南

### 目录结构

```
coffeeprism/
├── archetypes/      # 内容模板
├── assets/          # 原始资源文件
├── content/         # 网站内容
│   ├── posts/       # 博客文章
│   ├── coffee-beans/ # 咖啡豆介绍
│   ├── brewing-methods/ # 冲泡方法
│   └── coffee-equipment/ # 咖啡装备
├── layouts/         # 自定义布局
├── public/          # 生成的静态站点
├── resources/       # 缓存文件
├── scripts/         # 自动化脚本
├── static/          # 静态文件
└── themes/          # 主题
```

### 技术栈

- **Hugo**: 静态网站生成器
- **定制主题**: 基于PaperMod的自定义主题
- **Python**: 用于自动内容生成脚本
- **自动化工作流**: 用于自动化内容发布

### 代码规范

- 遵循 Hugo 和 Python 的最佳实践
- 保持代码简洁、可读
- 添加适当的注释

## 问题反馈

如果您发现bug或有功能建议，请通过以下方式提交：

1. 发送电子邮件至 feedback@coffeeprism.com
2. 描述问题或建议，提供尽可能多的上下文信息
3. 如果是bug报告，请提供复现步骤和环境信息

## 社区准则

- 保持尊重和专业
- 接受建设性批评
- 关注问题，而不是人
- 享受为咖啡社区做贡献的过程

感谢您为Coffee Prism做出的贡献！ 