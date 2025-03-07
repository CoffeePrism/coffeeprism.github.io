# Coffee Prism Website

A modern, responsive website for Coffee Prism, featuring a warm, cozy coffee shop theme with comprehensive information about coffee, brewing guides, and blog articles.

![Coffee Prism Website](assets/images/og-image.jpg)

## Features

- **Modern Design**: Elegant, warm, and minimalist coffee shop aesthetic
- **Responsive Layout**: Fully responsive design that works on all devices
- **Progressive Web App (PWA)**: Installable on mobile devices with offline support
- **Dark Mode**: Toggle between light and dark themes
- **Accessibility**: WCAG compliant with keyboard navigation and screen reader support
- **Performance Optimized**: Fast loading with optimized assets
- **SEO Friendly**: Proper meta tags, structured data, and semantic HTML

## Pages

- **Home**: Visually appealing landing page showcasing featured content
- **About**: Information about Coffee Prism's mission and team
- **Blog**: Articles about coffee brewing, origins, and equipment
- **Contact**: Contact form and information
- **Coffee**: Information about coffee beans and origins
- **Brewing**: Guides for brewing different types of coffee
- **Equipment**: Reviews and recommendations for coffee equipment

## Technologies Used

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS variables and Flexbox/Grid
- **JavaScript**: Interactive features and animations
- **Service Worker**: Offline support and caching
- **Font Awesome**: Icons
- **Google Fonts**: Typography

## Getting Started

### Prerequisites

- A modern web browser
- Basic knowledge of HTML, CSS, and JavaScript
- Git (for version control)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/CoffeePrism/coffeeprism.github.io.git
   cd coffeeprism.github.io
   ```

2. If you want to use Jekyll for local development:
   ```bash
   # Install Ruby and Jekyll
   gem install bundler jekyll

   # Install dependencies
   bundle install

   # Start the local server
   bundle exec jekyll serve
   ```

3. If you prefer to use a simple HTTP server:
   ```bash
   # Using Python
   python -m http.server 8000

   # Using Node.js
   npx serve
   ```

4. Open your browser and navigate to `http://localhost:8000` or `http://localhost:4000` (for Jekyll)

### File Structure

```
coffeeprism/
├── assets/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
├── _includes/
│   └── critical.css
├── _layouts/
│   ├── default.html
│   └── post.html
├── _posts/
│   └── blog articles in markdown
├── service-worker.js
├── manifest.json
├── index.html
├── about.html
├── blog.html
├── contact.html
├── offline.html
└── README.md
```

## Deployment

### GitHub Pages

This website is designed to be deployed on GitHub Pages:

1. Push your changes to the `main` branch:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. GitHub Actions will automatically build and deploy the site to GitHub Pages.

3. Your site will be available at `https://yourusername.github.io` or your custom domain if configured.

### Custom Domain Setup

To use a custom domain with GitHub Pages:

1. Purchase a domain from a domain registrar (e.g., Namecheap, GoDaddy).

2. In your GitHub repository, go to Settings > Pages > Custom domain and enter your domain.

3. Configure your domain's DNS settings:
   - For an apex domain (e.g., `coffeeprism.com`), add A records pointing to GitHub Pages IP addresses:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```
   - For a subdomain (e.g., `www.coffeeprism.com`), add a CNAME record pointing to `yourusername.github.io`.

4. Add a CNAME file to your repository with your domain name.

## Customization

### Changing Colors

The color scheme can be modified in `assets/css/style.css` by updating the CSS variables:

```css
:root {
  --dark-brown: #3a2618;
  --medium-brown: #6b4423;
  --light-brown: #a67c52;
  --cream: #f5f1e6;
  --beige: #e6d7c3;
  --off-white: #faf7f2;
  /* Add more color variables as needed */
}
```

### Adding New Pages

1. Create a new HTML file in the root directory (e.g., `new-page.html`).
2. Copy the structure from an existing page, including the header and footer.
3. Update the content as needed.
4. Add a link to the new page in the navigation menu in `_includes/header.html` or directly in each page's HTML.

### Adding Blog Posts

1. Create a new Markdown file in the `_posts` directory with the format `YYYY-MM-DD-title.md`.
2. Add front matter at the top of the file:
   ```yaml
   ---
   layout: post
   title: "Your Post Title"
   date: YYYY-MM-DD
   categories: [category1, category2]
   tags: [tag1, tag2]
   featured_image: /assets/images/your-image.jpg
   ---
   ```
3. Write your content in Markdown format below the front matter.

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Opera (latest)
- Mobile browsers (iOS Safari, Android Chrome)

## Performance Optimization

The website is optimized for performance:

- Minified CSS and JavaScript
- Optimized images
- Lazy loading for images
- Critical CSS inlined in the head
- Preloading of critical resources
- Service worker for caching and offline support

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Font Awesome for icons
- Google Fonts for typography
- Unsplash for stock images
- All coffee lovers and enthusiasts who contributed to the content

## Contact

For questions or feedback, please contact us at info@coffeeprism.com or visit our [contact page](https://www.coffeeprism.com/contact/).

---

Made with ☕ and ❤️ by Coffee Prism
