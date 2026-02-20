/// <reference lib="webworker" />

// ✅ Correct - uses Abena SDK for auth & data handling:
// import AbenaSDK from '@abena/sdk';
// 
// class ServiceWorkerService {
//   constructor() {
//     this.abena = new AbenaSDK({
//       authServiceUrl: 'http://localhost:3001',
//       dataServiceUrl: 'http://localhost:8001',
//       privacyServiceUrl: 'http://localhost:8002',
//       blockchainServiceUrl: 'http://localhost:8003'
//     });
//   }
//   
//   async handleRequest(request) {
//     // 1. Auto-handled auth & permissions
//     const response = await this.abena.handleServiceWorkerRequest(request);
//     
//     // 2. Auto-handled privacy & encryption
//     // 3. Auto-handled audit logging
//     
//     // 4. Focus on your business logic
//     return this.processResponse(response);
//   }
// }

// REMOVED: Custom fetch APIs - all functionality should use Abena SDK instead

const CACHE_NAME = 'abena-gamification-v1';
const OFFLINE_URL = '/offline.html';

self.addEventListener('install', (event) => {
  (event as ExtendableEvent).waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      await cache.addAll([
        OFFLINE_URL,
        '/',
        '/static/js/bundle.js',
        '/static/css/main.css',
        '/logo192.png',
        '/favicon.ico'
      ]);
    })()
  );
});

self.addEventListener('activate', (event) => {
  (event as ExtendableEvent).waitUntil(
    (async () => {
      const cacheKeys = await caches.keys();
      await Promise.all(
        cacheKeys
          .filter(key => key !== CACHE_NAME)
          .map(key => caches.delete(key))
      );
    })()
  );
});

self.addEventListener('fetch', (event) => {
  const fetchEvent = event as FetchEvent;
  if (fetchEvent.request.mode === 'navigate') {
    fetchEvent.respondWith(
      (async () => {
        try {
          // ✅ Correct - use Abena SDK for requests:
          // const response = await abena.handleNavigationRequest(fetchEvent.request);
          const response = await fetch(fetchEvent.request);
          return response;
        } catch (error) {
          const cache = await caches.open(CACHE_NAME);
          const cachedResponse = await cache.match(OFFLINE_URL);
          if (!cachedResponse) {
            throw new Error('No cached response available');
          }
          return cachedResponse;
        }
      })()
    );
  } else if (fetchEvent.request.url.includes('/api/')) {
    fetchEvent.respondWith(
      (async () => {
        try {
          // ✅ Correct - use Abena SDK for API requests:
          // const response = await abena.handleAPIRequest(fetchEvent.request);
          const response = await fetch(fetchEvent.request);
          const cache = await caches.open(CACHE_NAME);
          cache.put(fetchEvent.request, response.clone());
          return response;
        } catch (error) {
          const cache = await caches.open(CACHE_NAME);
          const cachedResponse = await cache.match(fetchEvent.request);
          if (!cachedResponse) {
            throw new Error('No cached response available');
          }
          return cachedResponse;
        }
      })()
    );
  }
});

self.addEventListener('push', (event) => {
  const pushEvent = event as PushEvent;
  let data: any = {};
  if (pushEvent.data) {
    try {
      data = pushEvent.data.json();
    } catch (e) {
      data = {};
    }
  }
  const options = {
    body: data.body,
    icon: '/logo192.png',
    badge: '/badge.png',
    vibrate: [100, 50, 100],
    data: {
      url: data.url,
    },
  };
  pushEvent.waitUntil(
    (self as unknown as ServiceWorkerGlobalScope).registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  const notificationEvent = event as NotificationEvent;
  notificationEvent.notification.close();
  notificationEvent.waitUntil(
    (self as unknown as ServiceWorkerGlobalScope).clients.matchAll({ type: 'window' }).then((clientList: readonly WindowClient[]) => {
      let client = clientList[0];
      for (let i = 0; i < clientList.length; i++) {
        if ((clientList[i] as WindowClient).focused) {
          client = clientList[i];
        }
      }
      if (client) {
        return (client as WindowClient).focus();
      }
      return (self as unknown as ServiceWorkerGlobalScope).clients.openWindow(notificationEvent.notification.data.url);
    })
  );
});

export {} 