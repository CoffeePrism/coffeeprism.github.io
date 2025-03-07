# Coffee Prism

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Coffee Prism is a website focused on coffee knowledge and product recommendations, built with Jekyll.

🌐 **Website**: [https://coffeeprism.com](https://coffeeprism.com)

## 🔍 Website Structure

The website consists of the following main components:

- **Blog Posts**: Located in the `_posts` directory
- **Coffee Topics**: Located in the `collections/_coffee` directory
- **Coffee Equipment**: Located in the `collections/_equipment` directory
- **Product Data**: Stored in the `_data/products.yml` file
- **Page Templates**: Located in the `_layouts` directory
- **Page Components**: Located in the `_includes` directory
- **Style Files**: Located in the `assets/css` directory
- **Images**: Located in the `assets/images` directory

## 📦 GitHub Pages Guidelines

This project uses standard GitHub Pages builds to automatically publish the website. The site is built directly from the `main` branch.

### Building Locally

To build and test the site locally, use the following command:

```bash
bundle exec jekyll serve
```

### Common Issues & Fixes

- **Template Errors**: Be careful when using Liquid filters like `slugify`. They should only be applied to strings, not arrays.
- **Dependency Conflicts**: Make sure to use the `github-pages` gem instead of directly depending on Jekyll for better compatibility.

## 📝 Contributing

Check out [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## 🖼️ Image Optimization

To improve website performance, ensure that uploaded images are optimized:

1. Image dimensions should be appropriate for their display size on the website
2. Use appropriate compression tools to reduce file size
3. Use consistent aspect ratios for product images (1:1 or 4:3 recommended)

## 📝 Issue Reporting

If you find a bug or have a feature request, please create an issue using our issue template.

## 📊 Project Status

This project is actively maintained and under development.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
