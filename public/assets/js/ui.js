/* Jalaram Computers — shared UI behaviour: splash + mobile drawer. */

/* ── Splash ── */
function initSplash() {
  const splash = document.getElementById('jc-splash');
  if (!splash) return;
  document.body.classList.add('jc-splash-active');

  let done = false;
  const dismiss = () => {
    if (done) return;
    done = true;
    splash.classList.add('is-hidden');
    document.body.classList.remove('jc-splash-active');
    sessionStorage.setItem('jc-splash-seen', '1');
    setTimeout(() => splash.remove(), 650);
  };

  // Seen this session, or the visitor prefers reduced motion → don't linger.
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (sessionStorage.getItem('jc-splash-seen') || reduce) {
    splash.style.transition = 'none';
    dismiss();
    return;
  }

  splash.addEventListener('click', dismiss);
  setTimeout(dismiss, 2400);
}

/* ── Mobile drawer ── */
function initDrawer() {
  const btn = document.getElementById('mobile-menu-btn');
  const drawer = document.getElementById('mobile-drawer');
  if (!btn || !drawer) return;

  const open = () => {
    drawer.classList.add('is-open');
    drawer.setAttribute('aria-hidden', 'false');
    btn.setAttribute('aria-expanded', 'true');
    document.body.classList.add('jc-drawer-open');
  };
  const close = () => {
    drawer.classList.remove('is-open');
    drawer.setAttribute('aria-hidden', 'true');
    btn.setAttribute('aria-expanded', 'false');
    document.body.classList.remove('jc-drawer-open');
  };

  btn.addEventListener('click', open);
  drawer.querySelectorAll('[data-drawer-close]').forEach((el) => el.addEventListener('click', close));
  drawer.querySelectorAll('.jc-drawer__nav a').forEach((a) => a.addEventListener('click', close));
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') close(); });
}

function init() { initSplash(); initDrawer(); }

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
