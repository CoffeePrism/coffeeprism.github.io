---
layout: default
title: About Us
permalink: /about/
---

<div class="about-page">
  <div class="container">
    <header class="page-header">
      <h1 class="page-title">About Coffee Prism</h1>
      <p class="page-description">Exploring the Colorful World of Coffee</p>
    </header>

    <div class="about-content">
      <div class="row">
        <div class="col-md-8">
          <div class="about-section card">
            <h2>Our Story</h2>
            <p>Coffee Prism was born from a love of coffee and a desire to share knowledge. As a group of coffee enthusiasts, we discovered that coffee is like a prism, able to refract a rich spectrum of flavors, cultures, and experiences. Through this platform, we hope to help more people explore the wonderful world of coffee, from the cultivation of coffee beans to the perfect drop in your cup.</p>

            <h2>Our Mission</h2>
            <p>Our mission is to provide accurate, practical coffee knowledge and product recommendations to help coffee lovers brew better coffee at home. Whether you're a coffee novice or a seasoned enthusiast, we aim to offer valuable information and advice for your coffee journey.</p>
          </div>
        </div>
        
        <div class="col-md-4">
          <div class="about-image card">
            <img src="{{ '/assets/images/about-coffee.jpg' | relative_url }}" alt="Coffee brewing" class="img-responsive">
          </div>
        </div>
      </div>
      
      <div class="about-section card">
        <h2>Our Content</h2>
        <div class="row">
          <div class="col-md-6">
            <div class="content-category">
              <i class="fas fa-book"></i>
              <h3>Coffee Knowledge</h3>
              <p>Comprehensive information on growing, processing, roasting, and brewing coffee</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="content-category">
              <i class="fas fa-globe-americas"></i>
              <h3>Coffee Origin Guides</h3>
              <p>Exploration of coffee regions around the world and their unique flavors</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="content-category">
              <i class="fas fa-coffee"></i>
              <h3>Equipment Reviews</h3>
              <p>Objective evaluations of various coffee equipment</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="content-category">
              <i class="fas fa-hand-paper"></i>
              <h3>Brewing Techniques</h3>
              <p>Detailed brewing guides and technique sharing</p>
            </div>
          </div>
          <div class="col-md-6">
            <div class="content-category">
              <i class="fas fa-shopping-cart"></i>
              <h3>Product Recommendations</h3>
              <p>Carefully selected coffee and coffee equipment recommendations</p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="about-section card">
        <h2>About Amazon Associates</h2>
        <p>To maintain the operation of our website, we have joined the Amazon Associates program. This means that when you purchase products through links on our website, we may earn a small commission at no additional cost to you. We only recommend products we truly believe in, and all reviews and recommendations are based on our genuine experience and research.</p>
      </div>

      <div class="row">
        <div class="col-md-6">
          <div class="about-section card">
            <h2>Contact Us</h2>
            <p>If you have any questions, suggestions, or cooperation intentions, please don't hesitate to contact us:</p>
            <p><strong>Email:</strong> <a href="mailto:info@coffeeprism.com">info@coffeeprism.com</a></p>
            <div class="contact-btn-container">
              <a href="{{ '/contact/' | relative_url }}" class="btn">Contact Us</a>
            </div>
          </div>
        </div>
        
        <div class="col-md-6">
          <div class="about-section card">
            <h2>Join Us</h2>
            <p>We welcome writers who are passionate about coffee to join our team. If you're interested in contributing content to Coffee Prism, please contact us through the above methods.</p>
            <div class="contact-btn-container">
              <a href="{{ '/contact/' | relative_url }}" class="btn btn-secondary">Become a Contributor</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<style>
  .about-content {
    margin-bottom: var(--spacing-xl);
  }
  
  .about-section {
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-lg);
  }
  
  .about-section h2 {
    color: var(--primary-color);
    margin-top: 0;
    margin-bottom: var(--spacing-md);
  }
  
  .about-image {
    padding: 0;
    overflow: hidden;
    height: 100%;
  }
  
  .about-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
  }
  
  .about-image:hover img {
    transform: scale(1.05);
  }
  
  .content-category {
    text-align: center;
    padding: var(--spacing-md);
    margin-bottom: var(--spacing-lg);
    transition: transform 0.3s ease;
  }
  
  .content-category:hover {
    transform: translateY(-5px);
  }
  
  .content-category i {
    font-size: 2.5rem;
    color: var(--accent-color);
    margin-bottom: var(--spacing-sm);
  }
  
  .content-category h3 {
    margin-top: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
    color: var(--secondary-color);
  }
  
  .contact-btn-container {
    margin-top: var(--spacing-md);
    text-align: center;
  }
</style> 