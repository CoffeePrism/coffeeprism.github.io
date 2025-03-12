/**
 * Image Fallback Handler for Coffee Prism
 * 
 * This script handles image loading errors and provides fallbacks for missing images.
 * It creates placeholder images dynamically when an image fails to load.
 */

document.addEventListener('DOMContentLoaded', function() {
  // Find all images on the page
  const images = document.querySelectorAll('img');
  
  // Add error handler to each image
  images.forEach(img => {
    img.addEventListener('error', function() {
      createPlaceholder(this);
    });
    
    // Force error check for images that might have already failed
    if (img.complete && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
      createPlaceholder(img);
    }
  });
  
  /**
   * Creates a placeholder for a failed image
   * @param {HTMLImageElement} img - The image element that failed to load
   */
  function createPlaceholder(img) {
    // Don't replace if already replaced
    if (img.getAttribute('data-placeholder-applied')) return;
    
    // Get image dimensions
    const width = img.width || 300;
    const height = img.height || 200;
    
    // Get image alt text for display
    const text = img.alt || 'Image';
    
    // Determine background color based on image path
    let color = '#8B5A2B'; // Default coffee brown
    
    if (img.src.includes('team-')) {
      color = '#6F4E37'; // Darker brown for team members
    } else if (img.src.includes('partner-')) {
      color = '#3A2618'; // Very dark brown for partners
    } else if (img.src.includes('flag-')) {
      // Different colors for different flags
      if (img.src.includes('ethiopia')) color = '#006600';
      else if (img.src.includes('colombia')) color = '#FFCC00';
      else if (img.src.includes('brazil')) color = '#009900';
      else if (img.src.includes('guatemala')) color = '#0066CC';
    }
    
    // Create SVG placeholder
    const svgContent = `
      <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
        <rect width="100%" height="100%" fill="${color}"/>
        <text x="50%" y="50%" font-family="Arial, sans-serif" font-size="14" fill="white" text-anchor="middle" dominant-baseline="middle">${text}</text>
      </svg>
    `;
    
    // Convert SVG to data URL
    const dataUrl = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgContent);
    
    // Set the image source to the data URL
    img.src = dataUrl;
    
    // Mark as replaced to avoid infinite loop
    img.setAttribute('data-placeholder-applied', 'true');
    
    // Log the replacement for debugging
    console.log(`Replaced missing image with placeholder: ${text}`);
  }
}); 