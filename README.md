# Coffee Prism

[![Jekyll site CI](https://github.com/your-username/coffeeprism/workflows/Jekyll%20site%20CI/badge.svg)](https://github.com/your-username/coffeeprism/actions)
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

## 📦 GitHub Actions Guidelines

This project uses GitHub Actions to automatically build and deploy the website. Follow these guidelines to ensure successful publishing:

> **Important Rule**: Always check if the GitHub Actions build was successful after pushing code. If the build fails, check the error logs and fix the issues.

### Build Status Verification Process:

1. Push changes to GitHub repository
2. Go to the [Actions page](https://github.com/CoffeePrism/coffeeprism.github.io/actions) to check the build status
3. If the build fails:
   - Click on the failed workflow to view detailed logs
   - Identify the error cause (usually Liquid template errors, dependency issues, or YAML front matter formatting errors)
   - Fix the issues locally and push the changes
   - Repeat these steps until the build succeeds

For more detailed information, please see the GitHub Actions workflow section in [CONTRIBUTING.md](CONTRIBUTING.md).

## 🔧 Cursor IDE Rules

This project includes custom rules for [Cursor IDE](https://cursor.sh/) to help developers avoid common errors and follow best practices:

- Reminders to check GitHub Actions build status after pushing code
- Checks for common Liquid template errors when saving files
- Prevention of using plugins not supported by GitHub Pages
- Reminders to test locally when modifying key files

These rules automatically take effect when editing this project with Cursor IDE. For detailed information, please see the [Cursor Rules Guide](docs/cursor-rules-guide.md).

## 🚀 How to Add New Content

### Adding Blog Posts

1. Create a new Markdown file in the `_posts` directory with the filename format `YYYY-MM-DD-title.md`
2. Add YAML front matter at the beginning of the file, for example:

```yaml
---
layout: post
title: "Article Title"
date: YYYY-MM-DD
author: Author Name
categories: [Category1, Category2]
tags: [Tag1, Tag2, Tag3]
featured: true/false
featured_image: /assets/images/image-name.jpg
excerpt: "Article summary"
---
```

3. Add the article content after the YAML front matter using Markdown format

### Adding Coffee Topics

1. Create a new Markdown file in the `collections/_coffee` directory
2. Add YAML front matter at the beginning of the file, for example:

```yaml
---
layout: coffee
title: "Coffee Name"
origin: "Origin"
roast_level: "Roast Level"
flavor_profile: ["Flavor1", "Flavor2", "Flavor3"]
tags: [Tag1, Tag2, Tag3]
featured_image: /assets/images/image-name.jpg
excerpt: "Brief description"
---
```

3. Add content after the YAML front matter using Markdown format

### Adding Coffee Equipment

1. Create a new Markdown file in the `collections/_equipment` directory
2. Add YAML front matter at the beginning of the file, for example:

```yaml
---
layout: equipment
title: "Equipment Name"
brand: "Brand"
type: "Equipment Type"
price_range: "Price Range"
tags: [Tag1, Tag2, Tag3]
featured_image: /assets/images/image-name.jpg
excerpt: "Brief description"
pros_cons:
  pros:
    - "Advantage 1"
    - "Advantage 2"
    - "Advantage 3"
  cons:
    - "Disadvantage 1"
    - "Disadvantage 2"
    - "Disadvantage 3"
---
```

3. Add content after the YAML front matter using Markdown format

### Adding Product Recommendations

1. Open the `_data/products.yml` file
2. Add a new product under the appropriate product category, for example:

```yaml
coffee_beans:
  - name: "Product Name"
    description: "Product Description"
    image: "/assets/images/products/image-name.jpg"
    price: "Price"
    amazon_id: "Amazon Product ID"
```

3. Ensure that the `amazon_id` is the correct Amazon product ID, which will be used to generate Amazon affiliate links

## 💻 Local Development

To run the website locally for development and testing, follow these steps:

1. Make sure Ruby and Bundler are installed
2. Clone the repository locally
3. Run `bundle install` in the project root directory to install dependencies
4. Run `bundle exec jekyll serve` to start the local server
5. Visit `http://localhost:4000` in your browser to view the website

## 🌐 Deployment

After pushing changes to the main branch, the website will be automatically built and deployed.

## 🖼️ Image Optimization

To improve website performance, ensure that uploaded images are optimized:

1. Image dimensions should be appropriate for their display size on the website
2. Use appropriate compression tools to reduce file size
3. Use consistent aspect ratios for product images (1:1 or 4:3 recommended)

## 🤝 Contributing Guidelines

We welcome contributions to improve Coffee Prism! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add some amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. Submit a **Pull Request**

Please make sure your code follows our style guide and passes all tests.

## 📝 Issue Reporting

If you find a bug or have a feature request, please create an issue using our issue template.

## 📊 Project Status

This project is actively maintained and under development.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
