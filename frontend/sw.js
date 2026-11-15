// LifeLink service worker: lets the app be installed on a phone and opens the page even with a weak connection.
// It never stores API answers (they hold private data). Files are fetched from the network first. Made by Krisanu.
const CACHE = 'lifelink-v2';
const FILES = ['/', '/index.html', '/css/style.css', '/js/i18n.js', '/js/i18n2.js', '/js/ui.js', '/js/pages.js', '/js/dashboards.js', '/js/main.js', '/icons/icon-192.png'];

self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin || url.pathname.startsWith('/api/')) return;
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
    return r;
  }).catch(() => caches.match(e.request).then(r => r || caches.match('/index.html'))));
});
