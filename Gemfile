source "https://rubygems.org"

# Use GitHub Pages gem
gem "github-pages", "~> 231", group: :jekyll_plugins

# Specify compatible versions of dependencies
gem "ffi", "~> 1.15.5" # Pin to older version compatible with RubyGems 3.1.6
gem "eventmachine", "1.2.7" # Pin eventmachine version for compatibility
gem "faraday", "~> 2.7.10" # Pin Faraday to avoid issues
gem "faraday-retry", "~> 2.1.0" # Specify version for retry middleware

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-paginate"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-github-metadata"
  gem "jekyll-multiple-languages-plugin"
end

# Platform-specific dependencies
platform :ruby do
  gem "webrick", "~> 1.7"
end

# Windows and JRuby-specific dependencies
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
  gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
end

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds since newer versions of the gem
# do not have a Java counterpart.
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]

# HTML Proofer for testing
gem "html-proofer", "~> 3.19" 