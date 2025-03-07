source "https://rubygems.org"

# Use Jekyll directly instead of github-pages gem for custom plugin support
gem "jekyll", "~> 4.3.2"

# Jekyll plugins
group :jekyll_plugins do
  gem "jekyll-paginate"
  gem "jekyll-sitemap"
  gem "jekyll-feed"
  gem "jekyll-seo-tag"
  gem "jekyll-github-metadata"
  gem "jekyll-multiple-languages-plugin"
end

# Windows and JRuby does not include zoneinfo files
platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

# Performance-booster for watching directories on Windows
gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]

# Lock `http_parser.rb` gem to `v0.6.x` on JRuby builds
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]

# Required for Ruby 3.0+
gem "webrick", "~> 1.8"

# Specify compatible versions of dependencies
gem "ffi", "~> 1.15.5" # Pin to older version compatible with RubyGems 3.1.6
gem "eventmachine", "1.2.7" # Pin eventmachine version for compatibility
gem "faraday", "~> 2.7.10" # Pin Faraday to avoid issues
gem "faraday-retry", "~> 2.1.0" # Specify version for retry middleware

# HTML Proofer for testing
gem "html-proofer", "~> 3.19" 