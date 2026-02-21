# [PWA] 프로그레시브 웹 앱 — Service Worker + Manifest

> 웹사이트를 마치 앱스토어에서 깐 앱처럼 만들어주는 기술.
> 폰 홈 화면에 아이콘을 추가할 수 있고, 인터넷이 끊겨도 작동한다.
> 앱스토어에 등록하지 않아도 되고, 웹사이트에 파일 2개(sw.js, manifest.json)만 추가하면 끝.

## manifest.json

```json
{
  "name": "앱 이름 2026",
  "short_name": "앱이름",
  "description": "한줄 설명",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3182f6",
  "icons": [
    {
      "src": "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='80'>🚀</text></svg>",
      "sizes": "any",
      "type": "image/svg+xml"
    }
  ]
}
```

## HTML 연결

```html
<link rel="manifest" href="/manifest.json">
<meta name="theme-color" content="#3182f6">
<meta name="apple-mobile-web-app-capable" content="yes">
```

## Service Worker (네트워크 우선)

```javascript
// sw.js
var CACHE_NAME = 'app-v1';

self.addEventListener('install', function(e) {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.map(function(k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function(e) {
  // HTML은 항상 네트워크 우선
  if (e.request.mode === 'navigate' || e.request.url.endsWith('.html') || e.request.url.endsWith('/')) {
    e.respondWith(
      fetch(e.request).catch(function() { return caches.match(e.request); })
    );
    return;
  }
  // 나머지는 네트워크 우선, 실패 시 캐시
  e.respondWith(
    fetch(e.request).then(function(res) {
      var clone = res.clone();
      caches.open(CACHE_NAME).then(function(cache) { cache.put(e.request, clone); });
      return res;
    }).catch(function() { return caches.match(e.request); })
  );
});
```

## SW 등록 + 캐시 정리

```javascript
if ('serviceWorker' in navigator) {
  // 이전 캐시 모두 삭제
  caches.keys().then(function(keys) {
    keys.forEach(function(k) { caches.delete(k); });
  });
  // 이전 SW 해제 후 재등록
  navigator.serviceWorker.getRegistrations().then(function(regs) {
    regs.forEach(function(r) { r.unregister(); });
    setTimeout(function() {
      navigator.serviceWorker.register('/sw.js');
    }, 500);
  });
}
```

## 삽질 방지

- **HTML은 반드시 네트워크 우선** — 캐시 우선이면 코드 업데이트가 반영 안 됨
- **SW 업데이트 후 `CACHE_NAME` 버전 올리기** — `v1` → `v2` 등
- **`skipWaiting()` + `clients.claim()`** — 새 SW 즉시 활성화
- **캐시 정리 코드 필수** — 이전 SW가 오래된 HTML을 캐싱하고 있을 수 있음
- **아이콘은 SVG 이모지로** — 별도 이미지 파일 없이 `data:image/svg+xml` 사용
- **iOS Safari** — `apple-mobile-web-app-capable` 메타 태그 추가 필요
