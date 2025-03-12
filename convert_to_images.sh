#!/bin/bash

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "ImageMagick is not installed. Please install it first."
    echo "On macOS: brew install imagemagick"
    echo "On Ubuntu/Debian: sudo apt-get install imagemagick"
    exit 1
fi

# Function to convert SVG to JPG/PNG
convert_svg_to_image() {
    local svg_file=$1
    local output_file=$2
    
    echo "Converting $svg_file to $output_file"
    convert "$svg_file" "$output_file"
    
    # Check if conversion was successful
    if [ $? -eq 0 ]; then
        echo "Successfully converted $svg_file to $output_file"
    else
        echo "Failed to convert $svg_file to $output_file"
    fi
}

# Find all SVG files created by the placeholder script and convert them
find assets/images -name "*.svg" | while read svg_file; do
    # Get the base name without extension
    base_name="${svg_file%.*}"
    
    # Determine the output format based on the original filename
    if [[ "$svg_file" == *".png.svg" ]]; then
        output_file="${base_name%.*}.png"
    else
        output_file="${base_name}.jpg"
    fi
    
    convert_svg_to_image "$svg_file" "$output_file"
done

# Convert the placeholder SVG files we just created
for file in assets/images/team-*.jpg assets/images/partner-*.png assets/images/flag-*.png \
            assets/images/about-*.jpg assets/images/coffee-*.jpg assets/images/equipment-*.jpg \
            assets/images/review-*.jpg assets/images/guide-*.jpg assets/images/blog-*.jpg \
            assets/images/author-*.jpg; do
    
    # Skip if the file doesn't exist
    if [ ! -f "$file" ]; then
        continue
    fi
    
    # Create a temporary SVG file
    temp_svg="${file}.svg"
    
    # Copy the content of the original file to the temporary SVG file
    cp "$file" "$temp_svg"
    
    # Convert the temporary SVG file to the original format
    convert_svg_to_image "$temp_svg" "$file"
    
    # Remove the temporary SVG file
    rm "$temp_svg"
done

echo "All SVG files have been converted to JPG/PNG format." 