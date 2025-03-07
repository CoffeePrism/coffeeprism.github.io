# Cursor Rules Guide

This document introduces the Cursor IDE rules configured for the Coffee Prism project, which are designed to help developers follow best practices and avoid common errors.

## What Are Cursor Rules?

Cursor rules are reminders and warnings set for the [Cursor IDE](https://cursor.sh/) that trigger when specific conditions are met (such as after saving files or executing Git commands). These rules help team members follow project conventions and avoid common mistakes.

## Rules Overview

Our Cursor rules mainly focus on the following aspects:

1. **GitHub Actions Monitoring** - Ensuring build status is checked after pushing changes
2. **Jekyll Template Checks** - Preventing common Liquid template errors
3. **YAML Format Validation** - Ensuring front matter is formatted correctly
4. **Dependency Validation** - Preventing the use of plugins not supported by GitHub Pages
5. **Best Practice Reminders** - Providing tips about local testing and documentation updates

## Main Rules Explained

### GitHub Actions Monitoring Reminder

This rule reminds you to check the build status after pushing changes:

```
reminder "GitHub Actions Verification" after git push {
  message: "🔍 Remember to check GitHub Actions build status at https://github.com/CoffeePrism/coffeeprism.github.io/actions"
  description: "Always verify your build completed successfully after pushing changes"
  severity: warning
}
```

### Jekyll Template Checks

These rules check for common template syntax issues:

```
warning on save **/**.html if content matches /\{\{.*\|.*slugify.*\}\}/ {
  message: "⚠️ Slugify Filter Usage: Check that you're applying slugify to strings, not arrays"
  description: "The slugify filter only works on strings. Arrays must be processed before slugifying."
}
```

### YAML Front Matter Validation

These rules ensure Jekyll front matter is correctly formatted:

```
warning on save **/_posts/*.md if not content matches /^---\n.*layout:.*\n.*title:.*\n.*date:.*\n.*categories:.*\n/ {
  message: "⚠️ Blog Post Front Matter: Missing required YAML front matter"
  description: "Posts should include layout, title, date, and categories in front matter"
}
```

### Dependency Management Rules

These rules ensure GitHub Pages compatibility:

```
warning on save Gemfile if content matches /gem "jekyll-multiple-languages-plugin"/ {
  message: "⚠️ Unsupported Plugin: jekyll-multiple-languages-plugin is not supported by GitHub Pages"
  description: "This plugin won't work on GitHub Pages. Consider using a supported alternative."
}
```

### GitHub Actions Workflow Rules

These rules ensure the GitHub Actions workflow is properly configured:

```
warning on save .github/workflows/*.yml if not content matches /permissions:/ {
  message: "⚠️ Missing permissions in GitHub Actions workflow"
  description: "GitHub Actions workflows need proper permissions to function correctly"
  severity: high
}
```

## How to Use Cursor Rules

1. **During Development**: The rules will automatically trigger when you save files or perform Git operations
2. **Addressing Warnings**: Carefully read the warning messages and make necessary corrections
3. **Leveraging Reminders**: Use the informational reminders to maintain good practices

## Adding New Rules

When adding new rules, follow these guidelines:

1. Make sure the rule addresses a real problem or best practice
2. Keep the message clear and concise
3. Include a detailed description that explains why the rule exists
4. Set appropriate severity level (info, warning, high)
5. Test the rule to ensure it triggers correctly

## Conclusion

Following these Cursor rules will help ensure consistent code quality and prevent common Jekyll site issues. The rules are designed to catch problems early, prompting you to fix them before they cause build failures. 