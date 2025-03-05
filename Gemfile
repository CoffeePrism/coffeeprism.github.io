source "https://rubygems.org"

# Use GitHub Pages gem
gem "github-pages", "~> 231", group: :jekyll_plugins

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-paginate"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
end

# Windows and JRuby does not include zoneinfo files, so bundle the tzinfo-data gem
# and associated library.
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock webrick to compatible version
gem "webrick", "~> 1.7"

# HTML Proofer for testing
gem "html-proofer", "~> 3.19"

# Add faraday-retry for GitHub Pages
gem "faraday-retry" 