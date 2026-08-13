/* Chunk Miner のサービスワーカー。
   目的は「電波のない移動中でも練習タブが動くこと」だけ。
   ネットワーク優先にしてあるので、デプロイした新版は次回起動時にそのまま反映される。 */

const V = 'cm-v4';
const ASSETS = [
  './',
  './index.html',
  './chunks.json',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(V).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== V).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  // Anthropic API と Google Fonts は触らない
  if (new URL(req.url).origin !== location.origin) return;

  /* HTML と chunks.json はブラウザの HTTP キャッシュを迂回して必ず取り直す。
     ネットワーク優先にしていても、fetch が既定のキャッシュ経路を通ると
     古い応答が返ることがあり、「デプロイしたのに端末に反映されない」の原因になる。
     画像やマニフェストは変わらないので通常の経路でよい。 */
  const fresh = req.mode === 'navigate' || /\/(index\.html|chunks\.json)$/.test(new URL(req.url).pathname);

  e.respondWith(
    fetch(fresh ? new Request(req, {cache:'reload'}) : req)
      .then(res => {
        const copy = res.clone();
        caches.open(V).then(c => c.put(req, copy));
        return res;
      })
      .catch(() => caches.match(req).then(hit =>
        hit || (req.mode === 'navigate' ? caches.match('./index.html') : Promise.reject())
      ))
  );
});
