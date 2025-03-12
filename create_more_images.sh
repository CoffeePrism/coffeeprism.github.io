#!/bin/bash

# Function to create a placeholder SVG image
create_placeholder() {
  local file=$1
  local width=$2
  local height=$3
  local text=$4
  local color=$5
  
  # Create the directory if it doesn't exist
  mkdir -p "$(dirname "$file")"
  
  # Create the SVG file
  cat > "$file" << EOF
<svg width="$width" height="$height" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="$color"/>
  <text x="50%" y="50%" font-family="Arial" font-size="14" fill="white" text-anchor="middle" dominant-baseline="middle">$text</text>
</svg>
EOF
  
  echo "Created placeholder: $file"
}

# Create more missing images
create_placeholder "assets/images/hero-bg.jpg" 1200 600 "Hero Background" "#6F4E37"
create_placeholder "assets/images/brewing-methods.jpg" 600 400 "Brewing Methods" "#8B5A2B"
create_placeholder "assets/images/author-alex.jpg" 100 100 "Alex" "#6F4E37"
create_placeholder "assets/images/favicon.png" 32 32 "CP" "#8B5A2B"
create_placeholder "assets/images/apple-touch-icon.png" 180 180 "CP" "#8B5A2B"
create_placeholder "assets/images/og-image.jpg" 1200 630 "Coffee Prism" "#8B5A2B"

# Blog thumbnails
create_placeholder "assets/images/blog-featured.jpg" 800 400 "Featured Blog" "#8B5A2B"
create_placeholder "assets/images/blog-latte-art.jpg" 400 300 "Latte Art" "#8B5A2B"
create_placeholder "assets/images/blog-coffee-origins.jpg" 400 300 "Coffee Origins" "#8B5A2B"
create_placeholder "assets/images/blog-water-quality.jpg" 400 300 "Water Quality" "#8B5A2B"

echo "Additional placeholder images have been created successfully!" 