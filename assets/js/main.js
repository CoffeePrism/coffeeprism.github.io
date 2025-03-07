document.addEventListener('DOMContentLoaded', function() {
  // Mobile navigation toggle
  const navTrigger = document.querySelector('.nav-trigger');
  if (navTrigger) {
    navTrigger.addEventListener('change', function() {
      document.body.classList.toggle('nav-open', this.checked);
    });
  }

  // Smooth scrolling for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    // Skip back-to-top button as it has its own handler
    if (anchor.closest('#back-to-top')) return;
    
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        window.scrollTo({
          top: targetElement.offsetTop,
          behavior: 'smooth'
        });
      }
    });
  });

  // Lazy loading images
  if ('loading' in HTMLImageElement.prototype) {
    // Browser supports native lazy loading
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    lazyImages.forEach(img => {
      img.src = img.dataset.src;
    });
  } else {
    // Fallback for browsers that don't support native lazy loading
    const lazyImages = document.querySelectorAll('.lazy-image');
    
    if (lazyImages.length > 0 && 'IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const image = entry.target;
            image.src = image.dataset.src;
            image.classList.remove('lazy-image');
            imageObserver.unobserve(image);
          }
        });
      });
      
      lazyImages.forEach(image => {
        imageObserver.observe(image);
      });
    }
  }

  // Product recommendation tracking
  window.trackProductClick = function(productName) {
    console.log('Product clicked:', productName);
    // Here you can add code to track clicks using analytics tools
    // For example: 
    // if (typeof gtag === 'function') {
    //   gtag('event', 'click', {
    //     'event_category': 'Product',
    //     'event_label': productName
    //   });
    // }
  };

  // Back to top button
  const backToTopButton = document.getElementById('back-to-top');
  if (backToTopButton) {
    // Show/hide the button based on scroll position
    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 300) {
        backToTopButton.classList.add('show');
      } else {
        backToTopButton.classList.remove('show');
      }
    });
    
    // Scroll to top when clicked
    backToTopButton.querySelector('a').addEventListener('click', function(e) {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
});

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/assets/js/service-worker.js')
      .then(registration => {
        console.log('ServiceWorker registration successful');
        
        // Request notification permission
        if ('Notification' in window) {
          Notification.requestPermission();
        }
        
        // Register periodic sync
        if ('periodicSync' in registration) {
          registration.periodicSync.register('cache-cleanup', {
            minInterval: 24 * 60 * 60 * 1000 // 24 hours
          });
        }
      })
      .catch(err => {
        console.log('ServiceWorker registration failed: ', err);
      });
  });
}

// Performance monitoring
const perfData = {
  navigationStart: performance.timing.navigationStart,
  loadEventEnd: performance.timing.loadEventEnd,
  domComplete: performance.timing.domComplete,
  domInteractive: performance.timing.domInteractive,
  domContentLoadedEventEnd: performance.timing.domContentLoadedEventEnd
};

// Send performance data to analytics
function sendPerformanceData() {
  const data = {
    pageLoadTime: perfData.loadEventEnd - perfData.navigationStart,
    domInteractive: perfData.domInteractive - perfData.navigationStart,
    domComplete: perfData.domComplete - perfData.navigationStart,
    domContentLoaded: perfData.domContentLoadedEventEnd - perfData.navigationStart
  };
  
  // Log performance data
  console.log('Performance metrics:', data);
  
  // Send to analytics if available
  if (window.ga) {
    ga('send', 'timing', 'Performance', 'Page Load', data.pageLoadTime);
    ga('send', 'timing', 'Performance', 'DOM Interactive', data.domInteractive);
    ga('send', 'timing', 'Performance', 'DOM Complete', data.domComplete);
  }
}

// Initialize performance monitoring
window.addEventListener('load', sendPerformanceData);

// Image lazy loading with IntersectionObserver
document.addEventListener('DOMContentLoaded', () => {
  if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
          }
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });

    document.querySelectorAll('img[loading="lazy"]').forEach(img => {
      imageObserver.observe(img);
    });
  }
});

// Form submission with background sync
function submitFormWithBackgroundSync(form) {
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    // Store form data
    const formData = new FormData(form);
    const data = {};
    for (let [key, value] of formData.entries()) {
      data[key] = value;
    }
    
    // Save to IndexedDB
    idb.set('sync-forms', data)
      .then(() => {
        return navigator.serviceWorker.ready;
      })
      .then(registration => {
        return registration.sync.register('sync-forms');
      })
      .then(() => {
        console.log('Background sync registered');
      })
      .catch(err => {
        console.error('Background sync failed:', err);
        // Fallback to normal form submission
        form.submit();
      });
  } else {
    // Fallback to normal form submission
    form.submit();
  }
}

// Handle form submissions
document.addEventListener('submit', event => {
  const form = event.target;
  if (form.hasAttribute('data-sync')) {
    event.preventDefault();
    submitFormWithBackgroundSync(form);
  }
});

// Add smooth scrolling
document.addEventListener('click', event => {
  if (event.target.matches('a[href^="#"]')) {
    event.preventDefault();
    const target = document.querySelector(event.target.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  }
});

// Theme switcher
function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem('theme', theme);
}

function initTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme) {
    setTheme(savedTheme);
  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
    setTheme('dark');
  }
}

// Initialize theme
initTheme();

// Listen for theme changes
window.matchMedia('(prefers-color-scheme: dark)').addListener(e => {
  setTheme(e.matches ? 'dark' : 'light');
});

// Handle theme toggle button
document.querySelector('.theme-toggle')?.addEventListener('click', () => {
  const currentTheme = document.documentElement.getAttribute('data-theme');
  setTheme(currentTheme === 'dark' ? 'light' : 'dark');
});

// Initialize tooltips
document.addEventListener('DOMContentLoaded', () => {
  const tooltips = document.querySelectorAll('[data-tooltip]');
  tooltips.forEach(element => {
    element.addEventListener('mouseenter', e => {
      const tooltip = document.createElement('div');
      tooltip.className = 'tooltip';
      tooltip.textContent = element.getAttribute('data-tooltip');
      document.body.appendChild(tooltip);
      
      const rect = element.getBoundingClientRect();
      tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
      tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
      
      element.addEventListener('mouseleave', () => {
        tooltip.remove();
      }, { once: true });
    });
  });
}); 