importScripts('https://unpkg.com/workbox-sw@2.1.2/build/importScripts/workbox-sw.prod.v2.1.2.js');

const workboxSW = new self.WorkboxSW({
  "cacheId": "hgtv",
  "skipWaiting": true,
  "clientsClaim": true
});

workboxSW.precache([]);

workboxSW.router.registerRoute(/^https?\:\/\/static.*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

//For development setup caching of assets
workboxSW.router.registerRoute(/^http:\/\/localhost:5000\/static/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?\:\/\/ajax.googleapis.com\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?:\/\/cdnjs.cloudflare.com\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?:\/\/images\.hasgeek\.com\/embed\/file\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?:\/\/imgee\.s3\.amazonaws\.com\/imgee\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?:\/\/fonts.googleapis.com\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(/^https?:\/\/fonts.gstatic.com\/*/, workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

workboxSW.router.registerRoute(new RegExp('http://localhost:8000/'), workboxSW.strategies.networkFirst({
  cacheName: 'routes'
}), 'GET');

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('routes')
      .then(cache => cache.add('http://localhost:8000/'))
  );
});
