#!/bin/bash

# Create directories for missing images
mkdir -p assets/images/team
mkdir -p assets/images/partner
mkdir -p assets/images/flag
mkdir -p assets/images/blog
mkdir -p assets/images/coffee
mkdir -p assets/images/equipment
mkdir -p assets/images/author

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

# Team member images
create_placeholder "assets/images/team-alex.jpg" 300 300 "Alex Chen" "#6F4E37"
create_placeholder "assets/images/team-maya.jpg" 300 300 "Maya Rodriguez" "#6F4E37"
create_placeholder "assets/images/team-james.jpg" 300 300 "James Kim" "#6F4E37"
create_placeholder "assets/images/team-olivia.jpg" 300 300 "Olivia Johnson" "#6F4E37"

# Partner logos
create_placeholder "assets/images/partner-sca.png" 200 100 "SCA" "#3A2618"
create_placeholder "assets/images/partner-fair-trade.png" 200 100 "Fair Trade" "#3A2618"
create_placeholder "assets/images/partner-rainforest.png" 200 100 "Rainforest Alliance" "#3A2618"
create_placeholder "assets/images/partner-direct-trade.png" 200 100 "Direct Trade" "#3A2618"

# Country flags
create_placeholder "assets/images/flag-ethiopia.png" 60 40 "Ethiopia" "#006600"
create_placeholder "assets/images/flag-colombia.png" 60 40 "Colombia" "#FFCC00"
create_placeholder "assets/images/flag-brazil.png" 60 40 "Brazil" "#009900"
create_placeholder "assets/images/flag-guatemala.png" 60 40 "Guatemala" "#0066CC"

# About page images
create_placeholder "assets/images/about-story.jpg" 600 400 "Our Story" "#8B5A2B"
create_placeholder "assets/images/about-mission.jpg" 600 400 "Our Mission" "#8B5A2B"

# Coffee page images
create_placeholder "assets/images/coffee-single-origin.jpg" 300 200 "Single Origin" "#8B5A2B"
create_placeholder "assets/images/coffee-blends.jpg" 300 200 "Coffee Blends" "#8B5A2B"
create_placeholder "assets/images/coffee-espresso.jpg" 300 200 "Espresso" "#8B5A2B"
create_placeholder "assets/images/coffee-decaf.jpg" 300 200 "Decaf" "#8B5A2B"
create_placeholder "assets/images/coffee-map.jpg" 800 500 "Coffee Map" "#8B5A2B"
create_placeholder "assets/images/coffee-processing.jpg" 600 400 "Coffee Processing" "#8B5A2B"

# Equipment page images
create_placeholder "assets/images/equipment-collection.jpg" 600 400 "Equipment Collection" "#8B5A2B"
create_placeholder "assets/images/equipment-grinders.jpg" 300 200 "Grinders" "#8B5A2B"
create_placeholder "assets/images/equipment-brewers.jpg" 300 200 "Brewers" "#8B5A2B"
create_placeholder "assets/images/equipment-kettles.jpg" 300 200 "Kettles" "#8B5A2B"
create_placeholder "assets/images/equipment-accessories.jpg" 300 200 "Accessories" "#8B5A2B"
create_placeholder "assets/images/equipment-maintenance.jpg" 600 400 "Maintenance" "#8B5A2B"

# Review images
create_placeholder "assets/images/review-baratza-encore.jpg" 400 300 "Baratza Encore" "#8B5A2B"
create_placeholder "assets/images/review-hario-v60.jpg" 400 300 "Hario V60" "#8B5A2B"
create_placeholder "assets/images/review-fellow-stagg.jpg" 400 300 "Fellow Stagg" "#8B5A2B"

# Guide images
create_placeholder "assets/images/guide-grinders.jpg" 300 200 "Grinder Guide" "#8B5A2B"
create_placeholder "assets/images/guide-espresso.jpg" 300 200 "Espresso Guide" "#8B5A2B"
create_placeholder "assets/images/guide-scales.jpg" 300 200 "Scale Guide" "#8B5A2B"

# Blog images
create_placeholder "assets/images/blog-coffee-roasting.jpg" 400 300 "Coffee Roasting" "#8B5A2B"
create_placeholder "assets/images/blog-pour-over-thumb.jpg" 200 150 "Pour Over" "#8B5A2B"
create_placeholder "assets/images/blog-espresso-thumb.jpg" 200 150 "Espresso" "#8B5A2B"
create_placeholder "assets/images/blog-coffee-myths-thumb.jpg" 200 150 "Coffee Myths" "#8B5A2B"
create_placeholder "assets/images/author-alex.jpg" 100 100 "Alex" "#8B5A2B"

# Convert SVG to JPG/PNG for browsers that might not support SVG
echo "Note: For production, you may want to convert these SVG files to JPG/PNG format."
echo "Placeholder images have been created successfully!" 