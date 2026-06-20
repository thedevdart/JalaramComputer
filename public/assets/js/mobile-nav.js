/**
 * Jalaram Computers — standalone mobile navigation drawer.
 * Loaded as a plain script (no module deps) so the hamburger always works.
 */
(function () {
  'use strict';

  const NAV_LINKS = [
    { href: '/', label: 'Home', key: 'home' },
    { href: '/shop', label: 'Shop', key: 'shop' },
    { href: '/services', label: 'Services', key: 'services' },
    { href: '/about', label: 'About', key: 'about' },
    { href: '/contact', label: 'Contact', key: 'contact' },
    { href: '/cart', label: 'Cart', key: 'cart' },
  ];

  let delegationBound = false;

  function clickPathHasMenuButton(e) {
    const path = e.composedPath ? e.composedPath() : [];
    for (const node of path) {
      if (node && node.id === 'mobile-menu-btn') return node;
      if (node && node.closest && node.closest('#mobile-menu-btn')) return node.closest('#mobile-menu-btn');
    }
    return e.target?.closest?.('#mobile-menu-btn') || null;
  }

  function findMenuButton() {
    return (
      document.getElementById('mobile-menu-btn') ||
      [...document.querySelectorAll('header button, sd-component button')].find((btn) => {
        if (btn.id === 'logout-btn' || btn.id === 'shop-filters-toggle') return false;
        const icon = btn.querySelector('iconify-icon');
        const name = icon?.getAttribute('icon') || '';
        return name.includes('menu');
      }) ||
      document.querySelector('header button.lg\\:hidden, sd-component button.lg\\:hidden')
    );
  }

  function ensureMenuButton() {
    const btn = findMenuButton();
    if (!btn) return null;
    btn.id = 'mobile-menu-btn';
    btn.type = 'button';
    btn.setAttribute('aria-label', 'Open menu');
    if (!btn.hasAttribute('aria-expanded')) btn.setAttribute('aria-expanded', 'false');
    if (!btn.dataset.jcMenuBound) {
      btn.dataset.jcMenuBound = 'true';
      const activate = (e) => {
        e.preventDefault();
        e.stopPropagation();
        toggleDrawer();
      };
      btn.addEventListener('click', activate);
      btn.addEventListener('touchend', activate, { passive: false });
    }
    return btn;
  }

  function getDrawer() {
    return document.getElementById('mobile-nav-drawer');
  }

  function openDrawer() {
    const drawer = getDrawer();
    if (!drawer) return;
    drawer.classList.remove('hidden-drawer');
    drawer.classList.add('active-drawer');
    document.body.style.overflow = 'hidden';
    findMenuButton()?.setAttribute('aria-expanded', 'true');
  }

  function closeDrawer() {
    const drawer = getDrawer();
    if (!drawer) return;
    drawer.classList.remove('active-drawer');
    drawer.classList.add('hidden-drawer');
    document.body.style.overflow = '';
    findMenuButton()?.setAttribute('aria-expanded', 'false');
  }

  function toggleDrawer() {
    const drawer = getDrawer();
    if (!drawer) {
      createDrawer();
      return toggleDrawer();
    }
    if (drawer.classList.contains('active-drawer')) closeDrawer();
    else openDrawer();
  }

  function createDrawer() {
    if (getDrawer()) return;

    const path = window.location.pathname;
    const activeKey = { '/': 'home', '/shop': 'shop', '/services': 'services', '/about': 'about', '/contact': 'contact', '/cart': 'cart' }[path];

    const linksHtml = NAV_LINKS.map((link) => {
      const active = link.key === activeKey ? ' text-accent font-semibold' : '';
      return `<a href="${link.href}" data-nav="${link.key}" class="py-3 text-silver hover:text-accent border-b border-white/5${active}">${link.label}</a>`;
    }).join('');

    const drawer = document.createElement('div');
    drawer.id = 'mobile-nav-drawer';
    drawer.className = 'fixed inset-0 z-[300] flex justify-end hidden-drawer';
    drawer.innerHTML = `
      <div id="mobile-drawer-backdrop" class="absolute inset-0 bg-slate-950/85 backdrop-blur-sm"></div>
      <div id="mobile-nav-drawer-content" class="relative w-80 max-w-[85vw] h-full bg-primary-dark shadow-2xl border-l border-white/5 flex flex-col z-10 p-6 overflow-y-auto" style="background-color:#0f172a">
        <div class="flex items-center justify-between mb-10 pb-6 border-b border-white/5">
          <a href="/" class="flex items-center gap-2">
            <img src="/assets/images/logo.png" alt="Jalaram Computers" class="h-10 w-auto">
          </a>
          <button type="button" id="mobile-drawer-close" class="text-silver hover:text-accent p-2" aria-label="Close menu">
            <iconify-icon icon="lucide:x" class="text-2xl"></iconify-icon>
          </button>
        </div>
        <div class="mb-6">
          <input type="search" id="mobile-nav-search" placeholder="Search products..." autocomplete="off">
        </div>
        <nav class="flex flex-col gap-2 text-sm uppercase tracking-[0.2em] font-medium" id="mobile-nav-list">
          ${linksHtml}
        </nav>
        <a href="/services" class="mobile-drawer-cta bg-accent text-primary-deeper mt-6" style="display:flex;align-items:center;justify-content:center;min-height:44px;padding:0.75rem 1rem;font-size:0.75rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;text-decoration:none;background:#d4af37;color:#091a2e;">Book a Service</a>
        <a href="https://wa.me/919892848643" target="_blank" rel="noopener" class="mobile-drawer-cta border border-green-600/40 text-green-400 mt-3" style="display:flex;align-items:center;justify-content:center;gap:0.5rem;min-height:44px;padding:0.75rem 1rem;font-size:0.75rem;text-decoration:none;">WhatsApp Us</a>
        <div class="pt-8 mt-auto border-t border-white/5 text-[10px] tracking-widest text-silver/40 uppercase text-center">
          Jalaram Computers &copy; ${new Date().getFullYear()}
        </div>
      </div>
    `;

    document.body.appendChild(drawer);

    drawer.querySelector('#mobile-drawer-close')?.addEventListener('click', closeDrawer);
    drawer.querySelector('#mobile-drawer-backdrop')?.addEventListener('click', closeDrawer);
    drawer.querySelectorAll('#mobile-nav-list a').forEach((a) => a.addEventListener('click', closeDrawer));

    const search = drawer.querySelector('#mobile-nav-search');
    if (search) {
      search.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          const q = search.value.trim();
          closeDrawer();
          window.location.href = q ? `/shop?search=${encodeURIComponent(q)}` : '/shop';
        }
      });
    }
  }

  function bindDelegation() {
    if (delegationBound) return;
    delegationBound = true;
    const handleMenuActivate = (e) => {
      const btn = clickPathHasMenuButton(e);
      if (!btn) return;
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
      toggleDrawer();
    };
    document.addEventListener('click', handleMenuActivate, true);
    document.addEventListener('touchend', handleMenuActivate, { capture: true, passive: false });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && getDrawer()?.classList.contains('active-drawer')) closeDrawer();
    });
  }

  function init() {
    ensureMenuButton();
    bindDelegation();
    createDrawer();
  }

  function scheduleInits() {
    init();
    setTimeout(init, 100);
    setTimeout(init, 400);
    setTimeout(init, 1200);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', scheduleInits);
  } else {
    scheduleInits();
  }

  function observeHeaderChanges() {
    if (!document.body || window.__jcMobileNavObserver) return;
    window.__jcMobileNavObserver = new MutationObserver(() => {
      if (findMenuButton()) ensureMenuButton();
    });
    window.__jcMobileNavObserver.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', observeHeaderChanges);
  } else {
    observeHeaderChanges();
  }

  window.jcMobileNav = { open: openDrawer, close: closeDrawer, toggle: toggleDrawer, init };
})();
