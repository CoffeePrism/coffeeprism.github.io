source "https://rubygems.org"

# Use GitHub Pages gem
gem "github-pages", "~> 231", group: :jekyll_plugins

# Specify compatible versions of dependencies
gem "ffi", "~> 1.15.5" # Pin to older version compatible with RubyGems 3.1.6

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-paginate"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
end

# Platform-specific dependencies
platform :ruby do
  gem "webrick", "~> 1.7"
  gem "faraday-retry"
end

# HTML Proofer for testing
gem "html-proofer", "~> 3.19"

# Windows and JRuby-specific dependencies
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", "~> 1.2"
  gem "tzinfo-data"
  gem "wdm", "~> 0.1.1"
end 