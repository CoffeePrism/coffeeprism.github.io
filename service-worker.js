/**
 * Coffee Prism - Service Worker
 * Provides offline support and caching for the website
 */

const CACHE_NAME = 'coffee-prism-v1';
const OFFLINE_PAGE = '/offline.html';

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/offline.html',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/images/logo.png',
  '/assets/images/hero-bg.jpg',
  '/assets/fonts/playfair-display-v30-latin-regular.woff2',
  '/assets/fonts/playfair-display-v30-latin-700.woff2',
  '/assets/fonts/montserrat-v25-latin-regular.woff2',
  '/assets/fonts/montserrat-v25-latin-700.woff2'
];

// Install event - precache assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => {
          return cacheName.startsWith('coffee-prism-') && cacheName !== CACHE_NAME;
        }).map(cacheName => {
          console.log('Deleting old cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // For HTML requests - network-first strategy
  if (event.request.headers.get('Accept').includes('text/html')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Cache the latest version
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // If network fails, try to serve from cache
          return caches.match(event.request)
            .then(cachedResponse => {
              if (cachedResponse) {
                return cachedResponse;
              }
              // If not in cache, serve the offline page
              return caches.match(OFFLINE_PAGE);
            });
        })
    );
    return;
  }

  // For other requests - cache-first strategy
  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Return cached response
          return cachedResponse;
        }

        // If not in cache, fetch from network
        return fetch(event.request)
          .then(response => {
            // Cache the response for future
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(cache => {
              // Only cache successful responses
              if (response.ok) {
                cache.put(event.request, responseClone);
              }
            });
            return response;
          })
          .catch(error => {
            // For image requests, return a fallback image
            if (event.request.url.match(/\.(jpg|jpeg|png|gif|svg)$/)) {
              return caches.match('/assets/images/image-placeholder.jpg');
            }
            
            // For other requests, just propagate the error
            throw error;
          });
      })
  );
});

// Background sync for form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'submit-form') {
    event.waitUntil(syncForms());
  }
});

// Push notification handling
self.addEventListener('push', event => {
  const data = event.data.json();
  
  const options = {
    body: data.body || 'New content available!',
    icon: '/assets/images/icon-192x192.png',
    badge: '/assets/images/badge-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title || 'Coffee Prism', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  event.waitUntil(
    clients.matchAll({type: 'window'})
      .then(windowClients => {
        const url = event.notification.data.url;
        
        // Check if there is already a window open with this URL
        for (const client of windowClients) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        
        // If not, open a new window
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});

// Helper function for form sync
async function syncForms() {
  try {
    // Get stored form data from IndexedDB
    // This is a simplified example - you would need to implement the actual IndexedDB operations
    const formData = await getStoredFormData();
    
    if (!formData || formData.length === 0) {
      return;
    }
    
    // Process each stored form submission
    const promises = formData.map(async (data) => {
      try {
        // Send the form data to the server
        const response = await fetch('/api/submit-form', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        });
        
        if (response.ok) {
          // If successful, remove from storage
          await removeFormData(data.id);
          return true;
        }
        return false;
      } catch (error) {
        console.error('Error syncing form:', error);
        return false;
      }
    });
    
    return Promise.all(promises);
  } catch (error) {
    console.error('Error in syncForms:', error);
    throw error;
  }
}

// Placeholder function for getting stored form data
// In a real implementation, this would use IndexedDB
function getStoredFormData() {
  return Promise.resolve([]);
}

// Placeholder function for removing form data
function removeFormData(id) {
  return Promise.resolve();
} 