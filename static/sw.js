/**
 * EduHub AI — High-Performance Service Worker (PWA) v2
 * Caches static core assets for instant load and offline resilience.
 * Uses Network-First for static assets to ensure zero stale cache issues.
 * API routes always bypass cache (network-only).
 */

const CACHE_NAME = 'eduhub-cache-v2';
const CORE_ASSETS = [
  '/',
  '/static/manifest.json',
  '/static/js/i18n.js?v=20260923_02',
  '/static/js/user-utils.js',
  '/static/js/doc-renderer.js',
  '/static/js/conversion-engine.js'
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(CORE_ASSETS).catch((err) => {
        console.warn('[SW] Cache addAll non-fatal warning:', err);
      });
    })
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[SW] Purging old cache:', key);
            return caches.delete(key);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Network-only for API requests and checkouts
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/health')) {
    return;
  }

  // Network-first, fallback to cache for static and locale files
  if (url.pathname.startsWith('/static/') || url.pathname.startsWith('/locales/')) {
    event.respondWith(
      fetch(event.request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
          const clone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return networkResponse;
      }).catch(() => {
        return caches.match(event.request);
      })
    );
    return;
  }

  // Network-first, fallback to cache for HTML navigation
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => {
        return caches.match('/');
      })
    );
  }
});

