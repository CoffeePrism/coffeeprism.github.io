const CACHE_NAME = 'coffee-prism-cache-v1';
const OFFLINE_URL = '/offline.html';

const urlsToCache = [
  '/',
  '/offline.html',
  '/assets/css/styles.css',
  '/assets/js/main.js',
  '/assets/images/favicon.png',
  '/assets/images/logo.png',
  '/assets/fonts/montserrat-v25-latin-regular.woff2',
  '/assets/fonts/montserrat-v25-latin-700.woff2'
];

// Install event - cache core assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', event => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }

        // Clone the request
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(response => {
          // Check if we received a valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          caches.open(CACHE_NAME)
            .then(cache => {
              // Don't cache if it's a data request
              if (!event.request.url.includes('/api/')) {
                cache.put(event.request, responseToCache);
              }
            });

          return response;
        }).catch(() => {
          // If the network is unavailable, try to return the offline page
          if (event.request.mode === 'navigate') {
            return caches.match(OFFLINE_URL);
          }
        });
      })
  );
});

// Background sync for offline form submissions
self.addEventListener('sync', event => {
  if (event.tag === 'sync-forms') {
    event.waitUntil(syncForms());
  }
});

// Push notification handling
self.addEventListener('push', event => {
  const options = {
    body: event.data.text(),
    icon: '/assets/images/icon-192x192.png',
    badge: '/assets/images/badge.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Details'
      },
      {
        action: 'close',
        title: 'Close'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Coffee Prism', options)
  );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Helper function to sync forms
async function syncForms() {
  try {
    const formData = await idb.get('sync-forms');
    if (!formData) return;

    const response = await fetch('/api/submit-form', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    });

    if (response.ok) {
      await idb.delete('sync-forms');
    }
  } catch (error) {
    console.error('Form sync failed:', error);
  }
}

// Cache management
async function trimCache(cacheName, maxItems = 50) {
  const cache = await caches.open(cacheName);
  const keys = await cache.keys();
  if (keys.length > maxItems) {
    await Promise.all(
      keys.slice(0, keys.length - maxItems).map(key => cache.delete(key))
    );
  }
}

// Periodic cache cleanup
self.addEventListener('periodicsync', event => {
  if (event.tag === 'cache-cleanup') {
    event.waitUntil(trimCache(CACHE_NAME));
  }
}); 