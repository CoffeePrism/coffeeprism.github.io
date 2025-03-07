source "https://rubygems.org"

# Use github-pages gem for GitHub Pages compatibility
gem "github-pages", "~> 231", group: :jekyll_plugins

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
gem "faraday-retry", "~> 2.1"

# HTML Proofer for testing
gem "html-proofer", "~> 3.19" 