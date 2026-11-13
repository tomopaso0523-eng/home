/* 旅の足跡 Service Worker
 * このファイルはビルド時に dist/sw.js として出力される（バージョンとプリキャッシュ一覧を埋め込む）。
 * キャッシュ名を変える場合は version が上がるので、古いキャッシュは activate で削除する。
 */
const VERSION = "b65678447a";
const CACHE = `tabinoashi-${VERSION}`;
const BASE = "/tabinoashi/"; // 公開パス（通常は "/"、minervalab.jp では "/tabinoashi/"）
const PRECACHE = [
  "/tabinoashi/",
  "/tabinoashi/assets/index-BJgFX992.css",
  "/tabinoashi/assets/index-DsFQ-6cW.js",
  "/tabinoashi/assets/mapData-Ds3_Hyq6.js",
  "/tabinoashi/assets/vendor-CrowJ5J7.js",
  "/tabinoashi/icons/apple-touch-icon.png",
  "/tabinoashi/icons/favicon-32.png",
  "/tabinoashi/icons/icon-192.png",
  "/tabinoashi/icons/icon-512.png",
  "/tabinoashi/index.html",
  "/tabinoashi/manifest.webmanifest"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) => cache.addAll(PRECACHE))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith("tabinoashi-") && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);

  // 画面遷移: ネットワーク優先、オフライン時はキャッシュしたHTML
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(BASE + "index.html", copy));
          return res;
        })
        .catch(() => caches.match(BASE + "index.html").then((r) => r || caches.match(BASE))),
    );
    return;
  }

  // 同一オリジンの静的ファイル: キャッシュ優先
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then(
        (hit) =>
          hit ||
          fetch(req).then((res) => {
            if (res.ok) {
              const copy = res.clone();
              caches.open(CACHE).then((c) => c.put(req, copy));
            }
            return res;
          }),
      ),
    );
    return;
  }

  // Webフォント: 取得できたものをキャッシュ（オフライン時は端末フォントで表示）
  if (url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com") {
    event.respondWith(
      caches.match(req).then(
        (hit) =>
          hit ||
          fetch(req)
            .then((res) => {
              const copy = res.clone();
              caches.open(CACHE).then((c) => c.put(req, copy));
              return res;
            })
            .catch(() => new Response("", { status: 504 })),
      ),
    );
  }
});
