# GitHub Actions 构建指南

本文档提供了详细的 GitHub Actions 工作流程指南，包括如何监控构建、排查常见问题以及修复构建错误。

## 构建流程概述

我们的 GitHub Actions 工作流程在 `.github/workflows/jekyll-custom-build.yml` 中定义，主要执行以下步骤：

1. 检出代码
2. 设置 Ruby 环境
3. 配置 GitHub Pages
4. 构建 Jekyll 站点
5. 上传构建产物
6. 部署到 GitHub Pages

## GitHub Actions 工作流配置要求

为确保 GitHub Actions 工作流正常运行，必须满足以下要求：

### 必要的权限设置

```yaml
permissions:
  contents: write  # 允许工作流修改仓库内容
  pages: write     # 允许工作流操作 GitHub Pages
  id-token: write  # 允许工作流使用 OIDC 令牌
```

### 必要的环境配置

```yaml
environment:
  name: github-pages
  url: ${{ steps.deployment.outputs.page_url }}
```

### 动作依赖关系

某些 GitHub Actions 动作依赖于其他动作。例如，`actions/upload-pages-artifact` 依赖于 `actions/upload-artifact`。确保包含所有必要的动作：

```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v2
  with:
    name: github-pages
    path: ./_site
    if-no-files-found: error

- name: Upload Pages artifact
  uses: actions/upload-pages-artifact@v2
  with:
    path: ./_site
```

> **重要注意事项**：我们发现 `actions/upload-artifact@v3` 在某些 GitHub Actions 运行环境中可能不可用或不稳定。强烈建议使用 `actions/upload-artifact@v2`，该版本更稳定且与 GitHub Pages 部署流程兼容性更好。

> **注意**：我们在 2023-03-07 解决了一个与 `actions/upload-artifact` 相关的构建错误。如果您看到类似的错误，请确保您的工作流包含上述所有必要的配置和依赖，并使用 v2 版本而非 v3。

## 监控构建状态

### 查看构建结果

每次推送代码到 `main` 分支后，都会触发自动构建。要查看构建状态：

1. 前往 [GitHub Actions 页面](https://github.com/CoffeePrism/coffeeprism.github.io/actions)
2. 找到最近的工作流运行记录
3. 查看其状态（成功、失败、进行中）

### 成功的构建

成功的构建会显示绿色对勾标记。此时，您的更改应已成功部署到 GitHub Pages 上。请访问 [www.coffeeprism.com](https://www.coffeeprism.com) 验证更改是否正确显示。

### 失败的构建

失败的构建会显示红色叉号。点击失败的工作流运行记录可以查看详细信息和错误日志。

## 常见错误类型及解决方案

### GitHub Actions 配置错误

**示例错误信息：**
```
Error: Missing download info for actions/upload-artifact@v3
```

**可能原因：**
- 缺少必要的动作依赖
- 权限配置不正确
- 环境配置缺失

**解决方法：**
1. 确保包含所有必要的动作和依赖
2. 设置正确的权限（contents, pages, id-token）
3. 配置适当的环境（github-pages）

### Liquid 模板错误

**示例错误信息：**
```
Liquid Exception: undefined method 'gsub' for #<Array:0x000000012fab4ed0> in index.html
```

**可能原因：** 
- 尝试对数组使用字符串方法
- 使用了未定义的变量
- 使用了不正确的过滤器

**解决方法：**
1. 检查相关文件中的 Liquid 语法
2. 确保 `slugify` 等过滤器只用于字符串
3. 修改类似于 `{% assign category_slug = category_item | slugify %}` 的代码，确保被过滤的对象是字符串

### YAML 前置配置错误

**示例错误信息：**
```
YAML Exception: mapping values are not allowed in this context at line 3 column 4
```

**可能原因：**
- YAML 格式错误
- 缩进不一致
- 特殊字符未正确处理

**解决方法：**
1. 检查 YAML 文件（如 `_config.yml`）或博客文章的前置配置
2. 确保所有键值对格式正确
3. 使用引号包裹包含特殊字符的值

### 插件兼容性问题

**示例错误信息：**
```
Bundler could not find compatible versions for gem "jekyll"
```

**可能原因：**
- 使用了 GitHub Pages 不支持的插件
- 插件版本冲突
- Gemfile 配置不正确

**解决方法：**
1. 检查 [GitHub Pages 支持的依赖版本](https://pages.github.com/versions/)
2. 移除不支持的插件
3. 更新 Gemfile 使用 `github-pages` gem 而非直接指定 Jekyll

### 文件路径问题

**示例错误信息：**
```
Error: could not read file /github/workspace/assets/css/main.css: no such file or directory
```

**可能原因：**
- 引用了不存在的文件
- 路径大小写错误
- 使用了绝对路径而非相对路径

**解决方法：**
1. 检查文件路径是否正确
2. 确保使用相对路径（如 `{{ '/assets/css/main.css' | relative_url }}`）
3. 验证所有引用的文件确实存在

## 本地测试技巧

在推送到 GitHub 前，建议执行以下本地测试：

```bash
# 安装依赖
bundle install

# 构建站点
bundle exec jekyll build --trace

# 如果希望在本地预览
bundle exec jekyll serve
```

如果本地构建成功，通常远程构建也会成功，但由于环境差异仍可能出现问题。

## 高级错误排查

### 查看详细构建日志

点击失败的工作流程，展开包含错误的步骤，查看完整日志输出。

### 查看原始日志文件

有时界面上的日志可能截断。点击右上角的"Download logs"下载完整日志文件进行分析。

### 使用 GitHub API 获取日志

可以使用 GitHub API 获取详细日志：

```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/CoffeePrism/coffeeprism.github.io/actions/runs/RUN_ID/logs
```

## 构建错误核对清单

在排查构建错误时，请检查以下常见问题：

- [ ] Liquid 模板语法错误
- [ ] 未定义变量或错误的变量类型
- [ ] YAML 前置配置格式问题
- [ ] 不支持的插件或依赖
- [ ] 文件路径错误
- [ ] 权限问题
- [ ] GitHub Pages 特定限制
- [ ] GitHub Actions 工作流配置错误
- [ ] 缺少必要的动作依赖

## 结论

遵循"检查构建状态→识别错误→修复问题→验证解决方案"的工作流程，可以确保网站始终保持正常构建和部署。养成每次推送后检查构建状态的习惯，将大大减少网站出现问题的可能性。 