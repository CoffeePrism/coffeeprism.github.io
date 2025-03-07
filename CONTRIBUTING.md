# Contributing to Coffee Prism

Thank you for considering contributing to Coffee Prism! This document outlines the process and guidelines for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## GitHub Actions Workflow

### Monitoring Build Status

After pushing changes to the repository, always follow these steps:

1. **Check Build Status**: 
   - Go to the [Actions tab](https://github.com/CoffeePrism/coffeeprism.github.io/actions) in the GitHub repository
   - Look for your recent commit in the workflow runs list
   - Wait for the build to complete and check its status (success or failure)

2. **If Build Succeeds**:
   - Verify the changes on the live site (https://www.coffeeprism.com)
   - Check for any visual or functional issues that may not have been caught by the build

3. **If Build Fails**:
   - Click on the failed workflow run to view details
   - Examine the error messages in the logs
   - Common issues include:
     - Liquid template errors (undefined variables, incorrect syntax)
     - Missing dependencies
     - YAML front matter formatting issues
     - File path issues
   - Make necessary fixes and commit them with a clear message
   - Push the changes and monitor the new build

### Troubleshooting Tips

#### Liquid Template Errors
- Check for undefined variables or incorrect variable types
- Ensure proper use of filters (e.g., `slugify` only works on strings, not arrays)
- Verify that arrays/collections are accessed correctly

#### Jekyll Build Issues
- Run `bundle exec jekyll build --trace` locally to get detailed error messages
- Check YAML front matter in all affected files
- Verify compatibility of plugins with GitHub Pages

#### GitHub Pages Limitations
- Remember that GitHub Pages only supports [certain gems and versions](https://pages.github.com/versions/)
- Avoid using unsupported plugins (like `jekyll-multiple-languages-plugin`)
- Use supported alternatives for custom functionality

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, please include as many details as possible using our bug report template.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. Before submitting an enhancement suggestion, please check the existing issues to avoid duplicates. When creating an enhancement suggestion, please include as many details as possible using our feature request template.

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Development Process

### Setting Up Your Development Environment

1. Clone your fork of the repository
2. Run `bundle install` to install dependencies
3. Run `bundle exec jekyll serve` to start the local development server

### Code Style Guidelines

#### Markdown

- Use ATX-style headers (with `#`)
- Use hyphens (`-`) for unordered lists
- Use exactly one blank line between sections

#### HTML/CSS

- Use 2 spaces for indentation
- Keep lines under 100 characters

#### YAML Front Matter

- Always include the required fields (layout, title, date)
- Keep fields in a consistent order

### Testing

Before submitting a pull request, make sure to test your changes locally.

## Additional Notes

### Issue and Pull Request Labels

We use labels to help organize and prioritize issues and pull requests. Here are some common labels:

- `bug`: Something isn't working
- `enhancement`: New feature or improvement
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers to the project

## Thank You!

Your contributions are what make the open-source community such a wonderful place to learn, inspire, and create. Any contributions you make are greatly appreciated. 