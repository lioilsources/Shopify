/// <reference types="@sveltejs/kit" />
/// <reference lib="webworker" />

// Minimální PWA service worker: cache-first pro statické soubory buildu,
// network-first pro vše ostatní (API, produkty).
import { build, files, version } from '$service-worker';

const sw = self as unknown as ServiceWorkerGlobalScope;
const CACHE = `chatshop-${version}`;
const ASSETS = [...build, ...files];

sw.addEventListener('install', (event) => {
	event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(ASSETS)));
});

sw.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
	);
});

sw.addEventListener('fetch', (event) => {
	if (event.request.method !== 'GET') return;
	const url = new URL(event.request.url);
	if (ASSETS.includes(url.pathname)) {
		event.respondWith(caches.match(event.request).then((hit) => hit ?? fetch(event.request)));
	}
});
