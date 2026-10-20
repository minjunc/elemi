"""Build the installable web app (PWA) into www/ from the game template."""
import json, base64, glob, os, re, shutil, hashlib

ROOT = '/home/claude'
WWW = 'www'
os.makedirs(f'{WWW}/fonts', exist_ok=True)

tpl = open(f'{ROOT}/game5_template.html').read()
art = {}
for f in sorted(glob.glob(f'{ROOT}/art/*.webp')):
    art[os.path.basename(f)[:-5]] = 'data:image/webp;base64,' + base64.b64encode(open(f, 'rb').read()).decode()
levels = [json.load(open(f'{ROOT}/levels5_w{w}.json')) for w in range(6)]
body = tpl.replace('__LEVELS__', json.dumps(levels, separators=(',', ':'))).replace('__ART__', json.dumps(art))

# ---- fonts: keep only the unicode chunks the game's text actually uses
used = set(ord(ch) for ch in body if ord(ch) > 0x7f) | set(range(0x20, 0x7f))
def in_range(rng):
    for part in rng.split(','):
        part = part.strip().replace('U+', '')
        if '-' in part:
            a, b = part.split('-')
            lo, hi = int(a, 16), int(b, 16)
        elif '?' in part:
            lo, hi = int(part.replace('?', '0'), 16), int(part.replace('?', 'f'), 16)
        else:
            lo = hi = int(part, 16)
        if any(lo <= u <= hi for u in used):
            return True
    return False
font_css = []
for fam, pkg in (('Jua', 'jua'), ('Gowun Dodum', 'gowun-dodum')):
    css = open(f'node_modules/@fontsource/{pkg}/400.css').read()
    for block in re.findall(r'@font-face\s*{[^}]*}', css):
        m = re.search(r'url\(\./files/([^)]+?\.woff2)\)', block)
        r = re.search(r'unicode-range:\s*([^;]+);', block)
        if not m or (r and not in_range(r.group(1))):
            continue
        fn = m.group(1)
        shutil.copy(f'node_modules/@fontsource/{pkg}/files/{fn}', f'{WWW}/fonts/{fn}')
        font_css.append(f"@font-face{{font-family:'{fam}';font-style:normal;font-display:swap;font-weight:400;src:url(fonts/{fn}) format('woff2');"
                        + (f"unicode-range:{r.group(1)};" if r else '') + '}')
open(f'{WWW}/fonts.css', 'w').write('\n'.join(font_css))

# ---- strip the artifact-only bits
body = re.sub(r'<title>.*?</title>\s*', '', body, count=1)
body = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', body)
body = re.sub(r'<link rel="preconnect"[^>]*>\s*', '', body)
body = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com[^>]*>\s*', '', body)

head = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<title>엘레미 테일즈</title>
<meta name="description" content="둥둥이가 원소 구슬을 먹고 변신해 길을 여는 귀여운 퍼즐 게임">
<meta name="theme-color" content="#EEF0FB">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="엘레미 테일즈">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" href="icons/favicon.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<link rel="stylesheet" href="fonts.css">
<style>
*, *::before, *::after { box-sizing: border-box; }
:root { padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
html { -webkit-text-size-adjust: 100%; overscroll-behavior: none; }
body { margin: 0; font: 14px/1.5 system-ui, sans-serif; overscroll-behavior: none; -webkit-user-select: none; user-select: none; -webkit-touch-callout: none; }
img { max-width: 100%; }
[hidden] { display: none !important; }
button { touch-action: manipulation; }
@media (hover: none) and (pointer: coarse) { .keys { display: none; } }
</style>
</head>
<body>
"""
tail = """
<script>
if ('serviceWorker' in navigator && window.isSecureContext && !window.Capacitor) {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}
</script>
</body>
</html>
"""
html = head + body + tail
open(f'{WWW}/index.html', 'w').write(html)

manifest = {
    'name': '엘레미 테일즈', 'short_name': '엘레미 테일즈',
    'description': '둥둥이가 원소 구슬을 먹고 변신해 길을 여는 귀여운 퍼즐 게임',
    'lang': 'ko', 'start_url': './', 'scope': './', 'display': 'standalone', 'orientation': 'portrait',
    'background_color': '#EEF0FB', 'theme_color': '#EEF0FB', 'categories': ['games', 'puzzle'],
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png'},
        {'src': 'icons/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'},
    ],
}
json.dump(manifest, open(f'{WWW}/manifest.webmanifest', 'w'), ensure_ascii=False, indent=2)

files = ['./', 'index.html', 'manifest.webmanifest', 'fonts.css'] + \
        [f'icons/{os.path.basename(p)}' for p in sorted(glob.glob(f'{WWW}/icons/*'))] + \
        [f'fonts/{os.path.basename(p)}' for p in sorted(glob.glob(f'{WWW}/fonts/*'))]
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
sw = f"""const CACHE = 'elemi-{ver}';
const FILES = {json.dumps(files)};
self.addEventListener('install', e => {{ e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(caches.match(e.request, {{ ignoreSearch: true }}).then(hit => hit || fetch(e.request).then(res => {{
    const copy = res.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return res;
  }}).catch(() => caches.match('index.html'))));
}});
"""
open(f'{WWW}/sw.js', 'w').write(sw)
print('index KB', len(html) // 1024, 'font files', len(glob.glob(f'{WWW}/fonts/*')),
      'fonts KB', sum(os.path.getsize(p) for p in glob.glob(f'{WWW}/fonts/*')) // 1024)
