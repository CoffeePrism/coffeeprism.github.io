# GitHub Actions Guide

This document provides a detailed guide for the GitHub Actions workflow, including how to monitor builds, troubleshoot common issues, and fix build errors.

## Build Process Overview

Our GitHub Actions workflow in `.github/workflows/jekyll-custom-build.yml` uses the standard GitHub Pages Jekyll workflow, which performs the following steps:

1. Checkout code
2. Setup GitHub Pages
3. Setup Ruby environment
4. Build Jekyll site
5. Upload build artifacts
6. Deploy to GitHub Pages

## GitHub Actions Workflow Requirements

To ensure GitHub Actions workflows run properly, the following requirements must be met:

### Required Permissions

```yaml
permissions:
  contents: read  # Allow the workflow to read repository contents
  pages: write    # Allow the workflow to operate GitHub Pages
  id-token: write # Allow the workflow to use OIDC tokens
```

### Concurrency Settings

```yaml
concurrency:
  group: "pages"
  cancel-in-progress: false
```

### Workflow Structure

We use the standard GitHub Pages Jekyll workflow, which contains two separate jobs for building and deployment:

```yaml
jobs:
  # Build job
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Setup Pages
        uses: actions/configure-pages@v3
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
      - name: Build with Jekyll
        run: bundle exec jekyll build
        env:
          JEKYLL_ENV: production
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v1

  # Deployment job
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```

> **Important Note**: We found that using custom workflows could lead to various issues. It is strongly recommended to use the standard Jekyll workflow provided by GitHub, which has been thoroughly tested and is fully compatible with GitHub Pages.

> **Note**: On 2023-03-07, we resolved a build error related to GitHub Actions workflow. The final solution was to adopt the standard GitHub Pages Jekyll workflow, which is the most reliable method.

## Monitoring Build Status

### Viewing Build Results

Each time you push code to the `main` branch, an automatic build is triggered. To view the build status:

1. Go to the [GitHub Actions page](https://github.com/CoffeePrism/coffeeprism.github.io/actions)
2. Find the most recent workflow run
3. Check its status (success, failure, in progress)

### Successful Builds

A successful build displays a green checkmark. Your changes should now be successfully deployed to GitHub Pages. Please visit [www.coffeeprism.com](https://www.coffeeprism.com) to verify that the changes are displaying correctly.

### Failed Builds

A failed build displays a red X. Click on the failed workflow run to view detailed information and error logs.

## Common Error Types and Solutions

### GitHub Actions Configuration Errors

**Example Error Message:**
```
Error: Missing download info for actions/upload-artifact@v3
```

**Possible Causes:**
- Missing necessary action dependencies
- Incorrect permission configuration
- Missing environment configuration

**Solutions:**
1. Ensure all necessary actions and dependencies are included
2. Set correct permissions (contents, pages, id-token)
3. Configure appropriate environment (github-pages)

### Liquid Template Errors

**Example Error Message:**
```
Liquid Exception: undefined method 'gsub' for #<Array:0x000000012fab4ed0> in index.html
```

**Possible Causes:** 
- Attempting to use string methods on arrays
- Using undefined variables
- Using incorrect filters

**Solutions:**
1. Check Liquid syntax in relevant files
2. Ensure filters like `slugify` are only used on strings
3. Modify code such as `{% assign category_slug = category_item | slugify %}` to ensure the filtered object is a string

### YAML Front Matter Errors

**Example Error Message:**
```
YAML Exception: mapping values are not allowed in this context at line 3 column 4
```

**Possible Causes:**
- YAML format errors
- Inconsistent indentation
- Special characters not properly handled

**Solutions:**
1. Check YAML files (such as `_config.yml`) or blog post front matter
2. Ensure all key-value pairs are formatted correctly
3. Use quotes to wrap values containing special characters

### Plugin Compatibility Issues

**Example Error Message:**
```
Bundler could not find compatible versions for gem "jekyll"
```

**Possible Causes:**
- Using plugins not supported by GitHub Pages
- Plugin version conflicts
- Incorrect Gemfile configuration

**Solutions:**
1. Check [GitHub Pages supported dependency versions](https://pages.github.com/versions/)
2. Remove unsupported plugins
3. Update Gemfile to use `github-pages` gem rather than directly specifying Jekyll

### File Path Issues

**Example Error Message:**
```
Error: could not read file /github/workspace/assets/css/main.css: no such file or directory
```

**Possible Causes:**
- Referencing non-existent files
- Case sensitivity errors in paths
- Using absolute paths instead of relative paths

**Solutions:**
1. Check if file paths are correct
2. Ensure you use relative paths (like `{{ '/assets/css/main.css' | relative_url }}`)
3. Verify all referenced files exist

## Local Testing Tips

Before pushing to GitHub, it's recommended to run the following local tests:

```bash
# Install dependencies
bundle install

# Build the site
bundle exec jekyll build --trace

# For local preview
bundle exec jekyll serve
```

If the local build succeeds, the remote build usually will too, but differences in environments may still cause issues.

## Advanced Error Troubleshooting

### Viewing Detailed Build Logs

Click on the failed workflow, expand the step containing the error, and view the complete log output.

### Viewing Raw Log Files

Sometimes logs on the interface may be truncated. Click the "Download logs" button in the top right corner to download the complete log file for analysis.

### Using GitHub API to Get Logs

You can use the GitHub API to get detailed logs:

```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/CoffeePrism/coffeeprism.github.io/actions/runs/RUN_ID/logs
```

## Build Error Checklist

When troubleshooting build errors, check the following common issues:

- [ ] Liquid template syntax errors
- [ ] Undefined variables or incorrect variable types
- [ ] YAML front matter formatting issues
- [ ] Unsupported plugins or dependencies
- [ ] File path errors
- [ ] Permission issues
- [ ] GitHub Pages specific limitations
- [ ] GitHub Actions workflow configuration errors
- [ ] Missing necessary action dependencies

## Conclusion

Following the "check build status → identify errors → fix issues → verify solution" workflow ensures your website always builds and deploys correctly. Creating a habit of checking build status after each push will greatly reduce the likelihood of issues with your website. 