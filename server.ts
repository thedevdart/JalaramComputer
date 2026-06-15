import compression from 'compression';
import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PUBLIC_DIR = path.join(__dirname, 'public');
const PORT = Number(process.env.PORT) || 3000;

app.use(compression({ threshold: 1024 }));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// =========================================================================
// --- CORE ROUTING SYSTEM -----------------------------------------------
// =========================================================================

const pageMapping: Record<string, string> = {
  '/': 'index.html',
  '/shop': 'shop.html',
  '/product': 'product.html',
  '/cart': 'cart.html',
  '/checkout': 'checkout.html',
  '/order-confirmed': 'order-confirmed.html',
  '/services': 'services.html',
  '/about': 'about.html',
  '/contact': 'contact.html',
  '/account': 'account.html',
  '/admin': 'admin.html',
  '/book-service': 'book-service.html',
};

const htmlToCleanRoute: Record<string, string> = {
  'index.html': '/',
  'shop.html': '/shop',
  'product.html': '/product',
  'cart.html': '/cart',
  'checkout.html': '/checkout',
  'order-confirmed.html': '/order-confirmed',
  'services.html': '/services',
  'about.html': '/about',
  'contact.html': '/contact',
  'account.html': '/account',
  'admin.html': '/admin',
};

app.use((req, res, next) => {
  const lowerPath = req.path.toLowerCase();
  if (req.path !== lowerPath && pageMapping[lowerPath]) {
    const queryString = req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : '';
    return res.redirect(301, lowerPath + queryString);
  }
  next();
});

app.use((req, res, next) => {
  const filename = req.path.startsWith('/') ? req.path.slice(1) : req.path;
  if (htmlToCleanRoute[filename]) {
    const queryString = req.url.includes('?') ? req.url.substring(req.url.indexOf('?')) : '';
    return res.redirect(301, htmlToCleanRoute[filename] + queryString);
  }
  next();
});

const DRAFT_ROUTES: [string, string][] = [
  ['f7e4c6a0-87e7-47fc-911b-bfa27489b88b', '/'],
  ['5c473e81-1a65-4639-91d8-15f5f4d65e1d', '/shop'],
  ['a9afe14c-897a-4d67-a3c3-f4bc987e5d42', '/product'],
  ['18c4be18-b393-429f-b284-37d56f69bb36', '/cart'],
  ['93544c81-424b-4e97-b308-0398e2a0ec47', '/checkout'],
  ['5873d4b7-b6d8-4ab1-b3d1-2ce455d6685f', '/order-confirmed'],
];

const HASH_PAGE_ROUTES: Record<string, string> = {
  '#services': '/services',
  '#about': '/about',
  '#contact': '/contact',
};

const HOME_HASHES = new Set([
  '#blog', '#faq',
  '#privacy', '#terms', '#refund', '#home',
]);

function resolveDraftUrl(raw: string): string {
  for (const [id, route] of DRAFT_ROUTES) {
    if (!raw.includes(id)) continue;
    const hashMatch = raw.match(/#([a-z0-9-]+)/i);
    const hash = hashMatch ? `#${hashMatch[1]}` : '';
    if (hash && HASH_PAGE_ROUTES[hash]) return HASH_PAGE_ROUTES[hash];
    if (hash && (route === '/' || HOME_HASHES.has(hash))) return `/${hash}`;
    return route;
  }
  return raw;
}

const replacements: { pattern: RegExp; replacement: string | ((substring: string, ...args: string[]) => string) }[] = [
  {
    pattern: /https:\/\/(?:draft-[a-f0-9-]+\.preview\.superdesign\.dev|p\.superdesign\.dev\/draft\/[a-f0-9-]+)[^"'\s>]*/gi,
    replacement: (match) => resolveDraftUrl(match),
  },
  { pattern: /(?:\.\/)?f7e4c6a0-87e7-47fc-911b-bfa27489b88b\.html/g, replacement: '/' },
  { pattern: /(?:\.\/)?5c473e81-1a65-4639-91d8-15f5f4d65e1d\.html/g, replacement: '/shop' },
  { pattern: /(?:\.\/)?a9afe14c-897a-4d67-a3c3-f4bc987e5d42\.html/g, replacement: '/product' },
  { pattern: /(?:\.\/)?18c4be18-b393-429f-b284-37d56f69bb36\.html/g, replacement: '/cart' },
  { pattern: /(?:\.\/)?93544c81-424b-4e97-b308-0398e2a0ec47\.html/g, replacement: '/checkout' },
  { pattern: /(?:\.\/)?5873d4b7-b6d8-4ab1-b3d1-2ce455d6685f\.html/g, replacement: '/order-confirmed' },
  { pattern: /\/\?t=\d+#?/g, replacement: '/' },
  { pattern: /href="\/#about"/g, replacement: 'href="/about"' },
  { pattern: /href="\/#contact"/g, replacement: 'href="/contact"' },
  { pattern: /\/#about/g, replacement: '/about' },
  { pattern: /\/#contact/g, replacement: '/contact' },
];

function stripSuperdesignDevScripts(html: string): string {
  let out = html;
  out = out.replace(/<meta name="preview-version"[^>]*>\s*/gi, '');
  out = out.replace(/<meta name="preview-timestamp"[^>]*>\s*/gi, '');
  out = out.replace(/<script type="module">import '\/__visual-edit-bridge\/iframe-runtime\.mjs[^']*';<\/script>/gi, '');
  out = out.replace(/<script src="\/assets\/js\/petite-vue\.iife\.js"><\/script>/gi, '');
  out = out.replace(/<script type="module">[\s\S]*?__SUPERDESIGN_PREVIEW__[\s\S]*?<\/script>/gi, '');
  out = out.replace(/<script type="module">[\s\S]*?\[SDComponent\] Runtime initialized[\s\S]*?<\/script>/gi, '');
  out = out.replace(/<style>\s*body\.sd-ready[\s\S]*?sd-component[\s\S]*?<\/style>/gi, '');
  out = out.replace(/body:not\(\.sd-ready\)\s*\{\s*opacity:\s*0\s*!important;\s*\}/gi, '');
  out = out.replace(/<!-- CINEMATIC PRE-LAUNCH[\s\S]*?id="jalaram-splash"[\s\S]*?<\/script>\s*/gi, '');
  out = out.replace(/<body class="sd-ready">/gi, '<body>');
  return out;
}

function processHtml(content: string): string {
  let replaced = stripSuperdesignDevScripts(content);
  for (const { pattern, replacement } of replacements) {
    replaced = typeof replacement === 'function'
      ? replaced.replace(pattern, replacement)
      : replaced.replace(pattern, replacement);
  }

  replaced = replaced.replace(/fonts-inter\.css/g, 'fonts-fast.css');
  replaced = replaced.replace(
    /<script src="\/assets\/js\/iconify-icon\.min\.js"><\/script>/gi,
    '<script src="/assets/js/iconify-icon.min.js" defer></script>'
  );

  replaced = replaced.replace(
    /<meta name="viewport" content="width=device-width, initial-scale=1\.0">/gi,
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">'
  );

  const perfHead = `<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="/assets/css/performance.css?v=1" id="jc-perf"><script src="/assets/js/performance.js?v=1" defer id="jc-perf-js"></script>`;
  if (!replaced.includes('performance.css')) {
    replaced = replaced.replace(/<\/head>/i, `${perfHead}</head>`);
  }

  replaced = replaced.replace(
    /<button(?![^>]*id="mobile-menu-btn")([^>]*class="[^"]*lg:hidden[^"]*"[^>]*)>\s*<iconify-icon icon="lucide:menu"/gi,
    '<button type="button" id="mobile-menu-btn" aria-label="Open menu" aria-expanded="false"$1><iconify-icon icon="lucide:menu"'
  );

  // Fix corrupted rupee symbol (?) → INR in static HTML prices
  replaced = replaced.replace(/>(\s*)\?([0-9])/g, '>$1&#8377;$2');
  replaced = replaced.replace(/Flat \?/g, 'Flat &#8377;');
  replaced = replaced.replace(/worth \?/gi, 'worth &#8377;');

  // Bump CSS cache versions on every served page so stale styles never linger
  replaced = replaced.replace(/performance\.css\?v=\d+/g, 'performance.css?v=2');
  replaced = replaced.replace(/mobile\.css\?v=\d+/g, 'mobile.css?v=10');

  const minimalCss = `<link rel="stylesheet" href="/assets/css/minimal.css" id="jc-minimal">`;
  const mobileCss = `<link rel="stylesheet" href="/assets/css/mobile.css?v=10" id="jc-mobile">`;
  if (!replaced.includes('minimal.css')) {
    replaced = replaced.replace(/<\/head>/i, `${minimalCss}</head>`);
  }
  if (!replaced.includes('mobile.css')) {
    replaced = replaced.replace(/<\/head>/i, `${mobileCss}</head>`);
  }

  const mobileNavScript = `<script src="/assets/js/mobile-nav.js?v=2" id="jc-mobile-nav"></script>`;
  const heroCacheScript = `<script>(function(){try{if(!localStorage.getItem('jalaram_hero_cache_migrated_v8')){['v4','v5','v6','v7'].forEach(function(v){localStorage.removeItem('jalaram_hero_slides_'+v);});localStorage.setItem('jalaram_hero_cache_migrated_v8','1');}}catch(e){}})();</script>`;
  const heroPreload = `<link rel="preload" as="image" href="/assets/images/hero/instant_support.webp" fetchpriority="high" media="(min-width: 768px)"><link rel="preload" as="image" href="/assets/images/hero/instant_support_mobile.webp" fetchpriority="high" media="(max-width: 767px)">`;
  if (!replaced.includes('instant_support.webp')) {
    replaced = replaced.replace(/<\/head>/i, `${heroPreload}</head>`);
  }
  if (!replaced.includes('mobile-nav.js')) {
    replaced = replaced.replace(/<\/head>/i, `${heroCacheScript}${mobileNavScript}</head>`);
  } else if (!replaced.includes('jalaram_hero_cache_migrated_v8')) {
    replaced = replaced.replace(/<\/head>/i, `${heroCacheScript}</head>`);
  }

  const interceptorScript = `<script type="module" src="/assets/js/cart-system.js" id="sd-interceptor"></script>`;

  const lastBodyRegex = /<\/body>(?![\s\S]*<\/body>)/i;
  if (lastBodyRegex.test(replaced)) {
    replaced = replaced.replace(lastBodyRegex, `${interceptorScript}</body>`);
  } else {
    replaced += interceptorScript;
  }

  return replaced;
}

const HERO_IMAGE_FALLBACKS: Record<string, string> = {
  'instant_support.jpg': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'instant_support_mobile.jpg': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
  'networking_support.jpg': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'networking_support_mobile.jpg': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
  'printers_repair.jpg': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'printers_repair_mobile.jpg': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
  'computer_repair.jpg': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'computer_repair_mobile.jpg': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
  'laptop_repair.jpg': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'laptop_repair_mobile.jpg': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
  'cctv_installation.jpg': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
  'cctv_installation_mobile.jpg': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
};

function heroLocalCandidates(file: string): string[] {
  const base = file.replace(/\.(webp|jpg|jpeg|png)$/i, '');
  const ext = path.extname(file).toLowerCase();
  const names = new Set<string>([file]);
  if (ext === '.webp') {
    names.add(`${base}.webp`);
    names.add(`${base}.jpg`);
    names.add(`${base.replace(/-/g, '_')}.webp`);
    names.add(`${base.replace(/-/g, '_')}.jpg`);
    names.add(`${base.replace(/_/g, '-')}.webp`);
    names.add(`${base.replace(/_/g, '-')}.jpg`);
  }
  return [...names];
}

app.get('/assets/images/hero/:file', (req, res) => {
  const file = req.params.file;
  for (const candidate of heroLocalCandidates(file)) {
    const local = path.join(PUBLIC_DIR, 'assets/images/hero', candidate);
    if (fs.existsSync(local)) {
      res.setHeader('Cache-Control', 'public, max-age=604800, immutable');
      return res.sendFile(local);
    }
  }
  const jpgFallback = HERO_IMAGE_FALLBACKS[file]
    || (file.endsWith('.webp') ? HERO_IMAGE_FALLBACKS[file.replace(/\.webp$/i, '.jpg')] : null)
    || (file.endsWith('.webp') ? HERO_IMAGE_FALLBACKS[file.replace(/\.webp$/i, '.jpg').replace(/-/g, '_')] : null);
  if (jpgFallback) return res.redirect(302, jpgFallback);
  const pngAsJpg = file.endsWith('.jpg') ? HERO_IMAGE_FALLBACKS[file.replace('.jpg', '.png')] : null;
  if (pngAsJpg) return res.redirect(302, pngAsJpg);
  res.status(404).end();
});

// Serve mapped HTML pages with link rewriting and cart-system injection
for (const [route, htmlFile] of Object.entries(pageMapping)) {
  app.get(route, (req, res) => {
    const filePath = path.join(PUBLIC_DIR, htmlFile);
    if (fs.existsSync(filePath)) {
      const originalHtml = fs.readFileSync(filePath, 'utf-8');
      const finalHtml = processHtml(originalHtml);
      res.setHeader('Content-Type', 'text/html');
      res.setHeader('Cache-Control', 'no-store, no-cache, must-revalidate, proxy-revalidate');
      res.setHeader('Pragma', 'no-cache');
      res.setHeader('Expires', '0');
      res.send(finalHtml);
    } else {
      res.status(404).send(`Page not found: ${htmlFile}`);
    }
  });
}

// Static assets with long-term caching (versioned filenames recommended)
app.use(express.static(PUBLIC_DIR, {
  maxAge: '7d',
  etag: true,
  setHeaders(res, filePath) {
    if (/\.(webp|jpg|jpeg|png|gif|svg|ico|woff2?)$/i.test(filePath)) {
      res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (/\.(css|js)$/i.test(filePath)) {
      res.setHeader('Cache-Control', 'public, max-age=604800');
    }
  },
}));

const server = app.listen(PORT, () => {
  console.log(`Jalaram Computers server listening on http://localhost:${PORT}`);
});

server.on('error', (err: NodeJS.ErrnoException) => {
  if (err.code === 'EADDRINUSE') {
    console.error(`\nPort ${PORT} is already in use.`);
    console.error('Another dev server is likely already running — open http://localhost:3000');
    console.error('To restart, stop the other process first (PowerShell):');
    console.error(`  Get-NetTCPConnection -LocalPort ${PORT} -State Listen | Select OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }\n`);
    process.exit(1);
  }
  throw err;
});
