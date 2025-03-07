/**
 * Coffee Prism - Main JavaScript
 * A modern, responsive coffee website
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize all components
  initNavigation();
  initLazyLoading();
  initAnimations();
  initThemeToggle();
  initBackToTop();
  initBrewingGuide();
  initProductGallery();
  initContactForm();
  
  // Register service worker for PWA support
  registerServiceWorker();
});

/**
 * Navigation functionality
 */
function initNavigation() {
  const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
  const navMenu = document.querySelector('.nav-menu');
  
  if (mobileMenuToggle && navMenu) {
    mobileMenuToggle.addEventListener('click', function() {
      navMenu.classList.toggle('active');
      document.body.classList.toggle('menu-open');
    });
    
    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.nav-menu') && !event.target.closest('.mobile-menu-toggle')) {
        if (navMenu.classList.contains('active')) {
          navMenu.classList.remove('active');
          document.body.classList.remove('menu-open');
        }
      }
    });
    
    // Add active class to current nav item
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
      const linkPath = link.getAttribute('href');
      if (currentLocation === linkPath || (linkPath !== '/' && currentLocation.startsWith(linkPath))) {
        link.classList.add('active');
      }
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          // Close mobile menu if open
          if (navMenu.classList.contains('active')) {
            navMenu.classList.remove('active');
            document.body.classList.remove('menu-open');
          }
          
          // Scroll to target
          window.scrollTo({
            top: targetElement.offsetTop - 80, // Adjust for header height
            behavior: 'smooth'
          });
        }
      });
    });
  }
}

/**
 * Lazy loading for images
 */
function initLazyLoading() {
  if ('IntersectionObserver' in window) {
    const lazyImages = document.querySelectorAll('img[loading="lazy"]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target;
          const src = img.getAttribute('data-src');
          
          if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.add('loaded');
          }
          
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px 0px',
      threshold: 0.01
    });
    
    lazyImages.forEach(img => {
      imageObserver.observe(img);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => {
      img.src = img.getAttribute('data-src');
      img.classList.add('loaded');
    });
  }
}

/**
 * Scroll animations
 */
function initAnimations() {
  if ('IntersectionObserver' in window) {
    const animatedElements = document.querySelectorAll('.fade-in, .slide-up');
    
    const animationObserver = new IntersectionObserver((entries, observer) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animated');
          observer.unobserve(entry.target);
        }
      });
    }, {
      rootMargin: '0px',
      threshold: 0.1
    });
    
    animatedElements.forEach(element => {
      // Add initial state class
      element.classList.add('animation-ready');
      animationObserver.observe(element);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    document.querySelectorAll('.fade-in, .slide-up').forEach(element => {
      element.classList.add('animated');
    });
  }
}

/**
 * Theme toggle functionality
 */
function initThemeToggle() {
  const themeToggle = document.querySelector('.theme-toggle');
  const htmlElement = document.documentElement;
  const themeIcon = themeToggle ? themeToggle.querySelector('i') : null;
  
  // Check for saved theme preference or respect OS preference
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  // Set initial theme
  if (savedTheme) {
    htmlElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme, themeIcon);
  } else if (prefersDark) {
    htmlElement.setAttribute('data-theme', 'dark');
    updateThemeIcon('dark', themeIcon);
  }
  
  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const currentTheme = htmlElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      htmlElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('theme', newTheme);
      
      updateThemeIcon(newTheme, themeIcon);
    });
  }
}

function updateThemeIcon(theme, iconElement) {
  if (!iconElement) return;
  
  if (theme === 'dark') {
    iconElement.classList.remove('fa-moon');
    iconElement.classList.add('fa-sun');
  } else {
    iconElement.classList.remove('fa-sun');
    iconElement.classList.add('fa-moon');
  }
}

/**
 * Back to top button
 */
function initBackToTop() {
  const backToTopButton = document.querySelector('.back-to-top');
  
  if (backToTopButton) {
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
      if (window.pageYOffset > 300) {
        backToTopButton.classList.add('visible');
      } else {
        backToTopButton.classList.remove('visible');
      }
    });
    
    // Scroll to top when clicked
    backToTopButton.addEventListener('click', function() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
}

/**
 * Interactive brewing guide
 */
function initBrewingGuide() {
  const brewingGuide = document.querySelector('.brewing-guide');
  
  if (brewingGuide) {
    const steps = brewingGuide.querySelectorAll('.brewing-step');
    const nextButtons = brewingGuide.querySelectorAll('.next-step');
    const prevButtons = brewingGuide.querySelectorAll('.prev-step');
    const progressBar = brewingGuide.querySelector('.progress-bar');
    
    let currentStep = 0;
    
    // Update progress bar
    function updateProgress() {
      if (progressBar) {
        const progress = ((currentStep + 1) / steps.length) * 100;
        progressBar.style.width = `${progress}%`;
      }
    }
    
    // Show current step
    function showStep(stepIndex) {
      steps.forEach((step, index) => {
        if (index === stepIndex) {
          step.classList.add('active');
        } else {
          step.classList.remove('active');
        }
      });
      
      updateProgress();
    }
    
    // Initialize first step
    showStep(currentStep);
    
    // Next button click
    nextButtons.forEach(button => {
      button.addEventListener('click', function() {
        if (currentStep < steps.length - 1) {
          currentStep++;
          showStep(currentStep);
        }
      });
    });
    
    // Previous button click
    prevButtons.forEach(button => {
      button.addEventListener('click', function() {
        if (currentStep > 0) {
          currentStep--;
          showStep(currentStep);
        }
      });
    });
    
    // Step navigation
    const stepNavItems = brewingGuide.querySelectorAll('.step-nav-item');
    stepNavItems.forEach((item, index) => {
      item.addEventListener('click', function() {
        currentStep = index;
        showStep(currentStep);
      });
    });
  }
}

/**
 * Product gallery with lightbox
 */
function initProductGallery() {
  const productGallery = document.querySelector('.product-gallery');
  
  if (productGallery) {
    const mainImage = productGallery.querySelector('.main-image img');
    const thumbnails = productGallery.querySelectorAll('.thumbnail');
    
    // Change main image when thumbnail is clicked
    thumbnails.forEach(thumbnail => {
      thumbnail.addEventListener('click', function() {
        const newSrc = this.getAttribute('data-src');
        const newAlt = this.getAttribute('alt');
        
        if (mainImage) {
          mainImage.src = newSrc;
          if (newAlt) mainImage.alt = newAlt;
          
          // Remove active class from all thumbnails
          thumbnails.forEach(thumb => thumb.classList.remove('active'));
          
          // Add active class to clicked thumbnail
          this.classList.add('active');
        }
      });
    });
    
    // Lightbox functionality
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox';
    lightbox.innerHTML = `
      <div class="lightbox-content">
        <img src="" alt="">
        <button class="lightbox-close">&times;</button>
      </div>
    `;
    document.body.appendChild(lightbox);
    
    const lightboxImg = lightbox.querySelector('img');
    const lightboxClose = lightbox.querySelector('.lightbox-close');
    
    // Open lightbox when main image is clicked
    if (mainImage) {
      mainImage.addEventListener('click', function() {
        lightboxImg.src = this.src;
        lightboxImg.alt = this.alt;
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
      });
    }
    
    // Close lightbox
    lightboxClose.addEventListener('click', function() {
      lightbox.classList.remove('active');
      document.body.style.overflow = '';
    });
    
    // Close lightbox when clicking outside the image
    lightbox.addEventListener('click', function(e) {
      if (e.target === lightbox) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
    
    // Close lightbox with Escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && lightbox.classList.contains('active')) {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
}

/**
 * Contact form validation and submission
 */
function initContactForm() {
  const contactForm = document.querySelector('.contact-form');
  
  if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Basic form validation
      let isValid = true;
      const nameInput = contactForm.querySelector('input[name="name"]');
      const emailInput = contactForm.querySelector('input[name="email"]');
      const messageInput = contactForm.querySelector('textarea[name="message"]');
      
      // Reset previous error messages
      contactForm.querySelectorAll('.error-message').forEach(error => error.remove());
      
      // Validate name
      if (!nameInput.value.trim()) {
        showError(nameInput, 'Please enter your name');
        isValid = false;
      }
      
      // Validate email
      if (!emailInput.value.trim()) {
        showError(emailInput, 'Please enter your email');
        isValid = false;
      } else if (!isValidEmail(emailInput.value)) {
        showError(emailInput, 'Please enter a valid email address');
        isValid = false;
      }
      
      // Validate message
      if (!messageInput.value.trim()) {
        showError(messageInput, 'Please enter your message');
        isValid = false;
      }
      
      if (isValid) {
        // Show loading state
        const submitButton = contactForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerHTML;
        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
        
        // Simulate form submission (replace with actual form submission)
        setTimeout(() => {
          // Show success message
          const successMessage = document.createElement('div');
          successMessage.className = 'alert alert-success';
          successMessage.innerHTML = '<i class="fas fa-check-circle"></i> Your message has been sent successfully!';
          
          contactForm.reset();
          contactForm.appendChild(successMessage);
          
          // Reset button
          submitButton.disabled = false;
          submitButton.innerHTML = originalButtonText;
          
          // Remove success message after 5 seconds
          setTimeout(() => {
            successMessage.remove();
          }, 5000);
        }, 1500);
      }
    });
    
    function showError(input, message) {
      const errorMessage = document.createElement('div');
      errorMessage.className = 'error-message';
      errorMessage.textContent = message;
      
      input.parentNode.appendChild(errorMessage);
      input.classList.add('error');
      
      // Remove error state on input
      input.addEventListener('input', function() {
        this.classList.remove('error');
        const error = this.parentNode.querySelector('.error-message');
        if (error) error.remove();
      });
    }
    
    function isValidEmail(email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(email);
    }
  }
}

/**
 * Service worker registration for PWA support
 */
function registerServiceWorker() {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
      navigator.serviceWorker.register('/service-worker.js')
        .then(function(registration) {
          console.log('Service Worker registered with scope:', registration.scope);
        })
        .catch(function(error) {
          console.log('Service Worker registration failed:', error);
        });
    });
  }
}

/**
 * Performance monitoring
 */
function reportPerformance() {
  if ('performance' in window && 'getEntriesByType' in performance) {
    window.addEventListener('load', function() {
      setTimeout(function() {
        const perfData = performance.getEntriesByType('navigation')[0];
        const lcpElement = performance.getEntriesByType('element')[0];
        
        const metrics = {
          // Navigation timing
          TTFB: perfData.responseStart - perfData.requestStart,
          FCP: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
          LCP: lcpElement?.startTime || 0,
          DCL: perfData.domContentLoadedEventEnd - perfData.fetchStart,
          Load: perfData.loadEventEnd - perfData.fetchStart,
          
          // Resource timing
          resources: performance.getEntriesByType('resource').length,
          resourcesSize: performance.getEntriesByType('resource').reduce((total, resource) => total + resource.transferSize, 0) / 1024
        };
        
        // Log performance metrics
        console.log('Performance Metrics:', metrics);
        
        // Send metrics to analytics (if available)
        if (typeof gtag === 'function') {
          gtag('event', 'performance', {
            'event_category': 'Performance',
            'event_label': 'Page Load',
            'value': Math.round(metrics.Load),
            'non_interaction': true
          });
        }
      }, 3000);
    });
  }
} 