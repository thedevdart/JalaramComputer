/* ═══════════════════════════════════════════════════════
   JALARAM COMPUTERS — Scroll Reveal Engine
   Auto-tags content and reveals it one-by-one on scroll.
   ═══════════════════════════════════════════════════════ */
(function () {
  'use strict';

  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return; // honor reduced motion — leave everything visible
  }

  // Elements we never animate (above-the-fold / chrome)
  var SKIP = 'header, footer, #services-hero, #jalaram-splash, sd-component[name="Header"], sd-component[name="Footer"]';

  function isInSkip(el) {
    return el.closest && el.closest(SKIP);
  }

  function tagSections() {
    var path = location.pathname;
    var isLanding = path === '/' || path === '/index.html' || path === '/index';
    if (!isLanding) return;
    var SKIP_SECTIONS = ['services-hero', 'hero-stats-bar'];
    document.querySelectorAll('section').forEach(function (s) {
      if (SKIP_SECTIONS.indexOf(s.id) !== -1) return;
      if (s.dataset.revealSection) return;
      s.classList.add('section-enter');
      s.dataset.revealSection = '1';
    });
  }

  function observeSections() {
    var sections = document.querySelectorAll('.section-enter');
    if (!sections.length) return;
    if (!('IntersectionObserver' in window)) {
      sections.forEach(function (s) { s.classList.add('is-visible'); });
      return;
    }
    var sio = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          sio.unobserve(entry.target);
        }
      });
    }, { threshold: 0.04, rootMargin: '0px 0px 0px 0px' });

    sections.forEach(function (s) {
      var r = s.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) {
        s.classList.add('is-visible');
      } else {
        sio.observe(s);
      }
    });
  }

  function tag() {
    // 1) Grids of cards → stagger their children in one-by-one
    var grids = document.querySelectorAll(
      '#featured-products-grid, #products-grid, ' +
      '#services .grid, .grid.sm\\:grid-cols-2, .grid.lg\\:grid-cols-3, ' +
      '.grid.lg\\:grid-cols-4, .grid.md\\:grid-cols-3'
    );
    grids.forEach(function (g) {
      if (isInSkip(g) || g.dataset.reveal) return;
      g.classList.add('reveal-stagger');
      g.dataset.reveal = '1';
    });

    // 2) Section headers, eyebrows, standalone blocks
    var blocks = document.querySelectorAll(
      'section h2, section .mb-16, section > div > p.max-w, ' +
      '.offer-card, .testimonial-card, .category-card, ' +
      '.glass-card, .glass-card-light, #booking-form-card, ' +
      '.contact-info-card, .about-stat-card, .info-card'
    );
    blocks.forEach(function (b) {
      if (isInSkip(b) || b.dataset.reveal || b.closest('.reveal-stagger')) return;
      b.classList.add('reveal');
      b.dataset.reveal = '1';
    });
  }

  function observe() {
    var targets = document.querySelectorAll('.reveal, .reveal-stagger');
    if (!('IntersectionObserver' in window)) {
      targets.forEach(function (t) { t.classList.add('is-visible'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });

    targets.forEach(function (t) {
      // Reveal immediately if already in view on load (no flash)
      var r = t.getBoundingClientRect();
      if (r.top < window.innerHeight * 0.92 && r.bottom > 0) {
        t.classList.add('is-visible');
      } else {
        io.observe(t);
      }
    });
  }

  function setupParallaxFreeze() {
    // Landing page only
    var path = location.pathname;
    var isLanding = path === '/' || path === '/index.html' || path === '/index';
    if (!isLanding) return;
    if (document.getElementById('jc-frozen-bg')) return;

    var bg = document.createElement('div');
    bg.id = 'jc-frozen-bg';
    bg.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(bg, document.body.firstChild);
    document.body.classList.add('jc-parallax');
  }

  function run() {
    setupParallaxFreeze();
    tagSections();
    observeSections();
    tag();
    observe();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', run);
  } else {
    run();
  }

  // Re-scan after dynamic content loads (products, etc.)
  var rescans = 0;
  var timer = setInterval(function () {
    run();
    if (++rescans >= 6) clearInterval(timer); // ~3s of rescans
  }, 500);

  window.jcReveal = run; // allow manual re-trigger
})();
