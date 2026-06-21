/* Home page — hero slideshow, stat counters, scroll-stack dots,
   featured products, newsletter. */
import { getProducts, subscribeNewsletter } from './api.js';
import { renderProducts } from './products.js';

/* ── 1. Hero slideshow ── */
const SLIDES = [
  { title: 'Instant Support',     subtitle: 'Remote & on-site IT help — same-day response for urgent issues', cta: 'Get Support',       link: '/services', align: 'left' },
  { title: 'Networking Support',  subtitle: 'Enterprise LAN, fiber links & structured cabling for offices',    cta: 'Network Solutions', link: '/services', align: 'right' },
  { title: 'Printers Repair',     subtitle: 'Printer sales, toner supply & on-site repair for businesses',      cta: 'Printer Services',  link: '/services', align: 'left' },
  { title: 'Computer Repair',     subtitle: 'Desktop diagnostics, upgrades & preventive maintenance',           cta: 'Repair My PC',      link: '/services', align: 'right' },
  { title: 'Laptop Repair',       subtitle: 'Screen, motherboard, RAM & SSD upgrades for all brands',           cta: 'Fix My Laptop',     link: '/services', align: 'left' },
  { title: 'CCTV Installation',   subtitle: 'HD cameras, DVR/NVR setup & remote monitoring for homes and offices', cta: 'Secure Your Space', link: '/services', align: 'right' },
];
const AUTOPLAY_MS = 4500;

function initHero() {
  const layers = [...document.querySelectorAll('.hero-bg-layer')];
  const dots = [...document.querySelectorAll('.hero-dot')];
  const overlay = document.getElementById('hero-bg-overlay');
  const wrap = document.getElementById('hero-content-wrap');
  const copy = document.getElementById('hero-heading-panel');
  const titleEl = document.getElementById('hero-title');
  const subEl = document.getElementById('hero-subtitle');
  const ctaEl = document.getElementById('hero-cta');
  if (!layers.length || !titleEl) return;

  let i = 0;
  let timer;

  function show(next, dir) {
    const s = SLIDES[next % SLIDES.length];
    next = next % SLIDES.length;
    layers.forEach((l, idx) => l.classList.toggle('active', idx === next));
    if (overlay) overlay.className = `hero-overlay-${s.align}`;
    if (wrap) wrap.className = `hero-content-${s.align}`;
    if (copy) copy.className = `jc-hero__copy hero-align-${s.align}`;
    titleEl.textContent = s.title;
    subEl.textContent = s.subtitle;
    if (ctaEl) { ctaEl.href = s.link; ctaEl.innerHTML = `${s.cta} <iconify-icon icon="lucide:arrow-right"></iconify-icon>`; }
    dots.forEach((d, idx) => d.classList.toggle('hero-dot--active', idx === next));

    if (copy) {
      const swap = dir === 'prev' ? 'hero-text-swap-right' : 'hero-text-swap-left';
      copy.classList.remove('hero-text-swap-left', 'hero-text-swap-right');
      void copy.offsetWidth;
      copy.classList.add(swap);
    }
    i = next;
  }

  function go(next, dir) { show(next, dir); restart(); }
  function restart() { clearInterval(timer); timer = setInterval(() => show(i + 1, 'next'), AUTOPLAY_MS); }

  dots.forEach((d, idx) => d.addEventListener('click', () => go(idx, idx > i ? 'next' : 'prev')));
  const prev = document.getElementById('hero-prev');
  const next = document.getElementById('hero-next');
  if (prev) prev.addEventListener('click', () => go((i - 1 + SLIDES.length) % SLIDES.length, 'prev'));
  if (next) next.addEventListener('click', () => go(i + 1, 'next'));

  const hero = document.getElementById('services-hero');
  if (hero) {
    hero.addEventListener('mouseenter', () => clearInterval(timer));
    hero.addEventListener('mouseleave', restart);
  }
  restart();
}

/* ── 2. Animated stat counters ── */
function countTo(el, end, suffix, decimals, duration) {
  if (!el || el.dataset.done) return;
  el.dataset.done = '1';
  let start = null;
  function step(ts) {
    if (!start) start = ts;
    const p = Math.min((ts - start) / duration, 1);
    const eased = p * (2 - p);
    el.textContent = (eased * end).toFixed(decimals) + suffix;
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = end.toFixed(decimals) + suffix;
  }
  requestAnimationFrame(step);
}
function runCounters() {
  countTo(document.getElementById('stat-uptime'), 99.9, '%', 1, 1600);
  countTo(document.getElementById('stat-nodes'), 12, 'K+', 0, 1800);
  countTo(document.getElementById('stat-projects'), 500, '+', 0, 2000);
}

/* ── 3. Scroll-stack dot navigation (desktop) ── */
function initStackNav() {
  const dots = [...document.querySelectorAll('.jc-dots__dot')];
  const panels = document.querySelectorAll('.jc-panel');
  if (!dots.length || !panels.length) return;
  const vh = () => window.innerHeight || document.documentElement.clientHeight || 1;
  function onScroll() {
    const idx = Math.min(Math.round(window.scrollY / vh()), panels.length - 1);
    dots.forEach((d, i) => d.classList.toggle('is-active', i === idx));
  }
  dots.forEach((dot, i) => dot.addEventListener('click', () => window.scrollTo({ top: i * vh(), behavior: 'smooth' })));
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ── 4. Featured products (live, with empty state) ── */
async function initFeatured() {
  const grid = document.getElementById('featured-products-grid');
  if (!grid) return;
  try {
    const products = await getProducts();
    const featured = products
      .slice()
      .sort((a, b) => (b.rating || 0) - (a.rating || 0))
      .slice(0, 4);
    if (!featured.length) {
      grid.innerHTML = `<div class="jc-empty jc-empty--span">
        <iconify-icon icon="lucide:package-open"></iconify-icon>
        <p>Our catalogue is being curated. Check back soon, or <a href="/contact">get in touch</a> for current stock.</p>
      </div>`;
      return;
    }
    renderProducts(grid, featured);
  } catch {
    grid.innerHTML = `<div class="jc-empty jc-empty--span"><p>Unable to load products right now.</p></div>`;
  }
}

/* ── 5. Newsletter ── */
function initNewsletter() {
  const form = document.getElementById('newsletter-form');
  const status = document.getElementById('newsletter-status');
  const btn = document.getElementById('newsletter-submit');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = (document.getElementById('newsletter-email') || {}).value || '';
    status.className = 'jc-news__status';
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      status.className = 'jc-news__status jc-news__status--error';
      status.textContent = 'Please enter a valid email address.';
      return;
    }
    if (btn) { btn.disabled = true; btn.textContent = 'Subscribing…'; }
    try {
      const data = await subscribeNewsletter(email);
      status.textContent = (data && data.message) || 'Thanks for subscribing!';
      form.reset();
    } catch (err) {
      status.className = 'jc-news__status jc-news__status--error';
      status.textContent = (err && err.message) || 'Something went wrong. Please try again.';
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = 'Subscribe'; }
    }
  });
}

function init() {
  initHero();
  runCounters();
  initStackNav();
  initFeatured();
  initNewsletter();
}
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
else init();
