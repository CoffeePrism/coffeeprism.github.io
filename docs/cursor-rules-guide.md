# Cursor Rules Guide

本文档介绍了 Coffee Prism 项目中配置的 Cursor IDE 规则，这些规则旨在帮助开发者遵循最佳实践并避免常见错误。

## 什么是 Cursor 规则？

Cursor 规则是针对 [Cursor IDE](https://cursor.sh/) 设置的提醒和警告，当满足特定条件时（例如保存文件或执行 Git 命令后）会触发。这些规则帮助团队成员遵循项目约定并避免常见错误。

## 规则概览

我们的 Cursor 规则主要聚焦于以下几个方面：

1. **GitHub Actions 监控** - 确保在推送更改后检查构建状态
2. **Jekyll 模板检查** - 防止常见的 Liquid 模板错误
3. **YAML 格式验证** - 确保前置配置格式正确
4. **依赖项验证** - 防止使用 GitHub Pages 不支持的插件
5. **最佳实践提醒** - 提供有关本地测试和文档更新的提示

## 主要规则详解

### GitHub Actions 监控提醒

```
reminder "GitHub Actions Verification" after git push {
  message: "🔍 Remember to check GitHub Actions build status"
  severity: warning
}
```

**作用**：每次推送代码后提醒你检查 GitHub Actions 构建状态。这是项目的重要规则，确保你会在每次推送后验证构建是否成功。

### Liquid 模板语法检查

```
warning on save **/**.html if content matches /\{\{.*\|.*slugify.*\}\}/ {
  message: "⚠️ Slugify Filter Usage: Check that you're applying slugify to strings, not arrays"
}
```

**作用**：当你在 HTML 文件中使用 `slugify` 过滤器时，提醒你确保只对字符串使用该过滤器，而不是数组。这可以防止 `undefined method 'gsub' for Array` 错误。

### 插件兼容性检查

```
warning on save Gemfile if content matches /gem "jekyll-multiple-languages-plugin"/ {
  message: "⚠️ Unsupported Plugin: jekyll-multiple-languages-plugin is not supported by GitHub Pages"
}
```

**作用**：防止添加 GitHub Pages 不支持的插件，这会导致远程构建失败。

### 本地测试提醒

```
reminder on save [_config.yml, **/_layouts/*, **/_includes/*] {
  message: "🔄 Remember to test your build locally with 'bundle exec jekyll build --trace'"
  severity: info
}
```

**作用**：当修改关键文件后，提醒你在本地测试构建，以便在推送前捕获错误。

## 如何获取规则提醒

使用 Cursor IDE 编辑项目代码时，规则会以通知的形式显示：

- **警告**（⚠️）- 表示潜在的问题，需要注意
- **提醒**（🔍）- 提示你执行某些操作
- **信息**（ℹ️）- 提供有用的上下文信息

## 自定义规则

如果你想添加或修改规则，可以编辑项目根目录中的 `.cursorrules` 文件。规则使用简单的声明式语法，格式为：

```
[rule_type] [trigger] [condition] {
  message: "显示的消息"
  description: "更详细的描述"
  severity: [info|warning|error]
}
```

## 推荐工作流程

使用这些规则的理想工作流程是：

1. 进行代码修改
2. 注意 Cursor 提供的实时警告和提示
3. 在本地测试构建 (`bundle exec jekyll build --trace`)
4. 提交并推送更改
5. 根据推送后的提醒，检查 GitHub Actions 构建状态
6. 如果构建失败，检查错误日志并修复问题

## 结论

Cursor 规则是确保项目稳定性的辅助工具，它们与我们的 GitHub Actions 监控指南相辅相成。通过遵循这些规则和提示，你可以减少构建错误并提高开发效率。 