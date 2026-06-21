/* Account portal — sign in / register / order history (Django session auth). */
import { authMe, authLogin, authRegister, authLogout, authGoogle, getMyOrders, formatINR } from './api.js';
import { esc } from './products.js';

const root = document.getElementById('account-root');
const profileDot = document.getElementById('header-profile-dot');
const googleClientId = root?.dataset.googleClientId || '';

let googleScriptPromise = null;

function loadGoogleScript() {
  if (window.google?.accounts?.id) return Promise.resolve();
  if (googleScriptPromise) return googleScriptPromise;
  googleScriptPromise = new Promise((resolve, reject) => {
    const existing = document.querySelector('script[data-jc-google]');
    if (existing) {
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => reject(new Error('Google sign-in failed to load.')), { once: true });
      return;
    }
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.dataset.jcGoogle = '1';
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Google sign-in failed to load.'));
    document.head.appendChild(script);
  });
  return googleScriptPromise;
}

function showGoogleError(message) {
  const loginErr = document.getElementById('login-error');
  const registerErr = document.getElementById('register-error');
  const activeErr = loginErr && !document.getElementById('login-form')?.hidden ? loginErr : registerErr;
  if (activeErr) activeErr.textContent = message;
}

async function initGoogleSignIn(onSuccess) {
  if (!googleClientId) return;

  const host = document.getElementById('google-signin-host');
  if (!host) return;

  try {
    await loadGoogleScript();
    google.accounts.id.initialize({
      client_id: googleClientId,
      callback: async (response) => {
        showGoogleError('');
        host.classList.add('is-busy');
        try {
          const user = await authGoogle(response.credential);
          onSuccess(user);
        } catch (ex) {
          showGoogleError((ex && ex.message) || 'Google sign-in failed.');
          host.classList.remove('is-busy');
        }
      },
      auto_select: false,
      cancel_on_tap_outside: true,
    });
    const width = Math.min(host.offsetWidth || 320, 400);
    google.accounts.id.renderButton(host, {
      type: 'standard',
      theme: 'outline',
      size: 'large',
      text: 'continue_with',
      shape: 'rectangular',
      logo_alignment: 'left',
      width,
    });
  } catch (ex) {
    host.innerHTML = `<p class="jc-auth__error">${esc((ex && ex.message) || 'Google sign-in unavailable.')}</p>`;
  }
}

function initials(user) {
  const name = user.displayName || user.email || 'U';
  return name.split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase();
}

function setProfileDot(active) {
  if (!profileDot) return;
  profileDot.hidden = !active;
}

function statusTone(status) {
  const s = (status || '').toLowerCase();
  if (s.includes('paid') || s.includes('deliver')) return 'ok';
  if (s.includes('cancel') || s.includes('fail')) return 'err';
  return 'pending';
}

function authView() {
  setProfileDot(false);
  root.innerHTML = `<div class="jc-account__card jc-auth">
    <div class="jc-auth__brand">
      <div class="jc-auth__brand-top">
        <img src="/assets/images/logo.png?v=3" alt="" class="jc-auth__logo" width="120" height="48">
        <div>
          <strong>Jalaram Computers</strong>
          <span>Mumbai's trusted IT partner</span>
        </div>
      </div>
      <ul class="jc-auth__features">
        <li><iconify-icon icon="lucide:package"></iconify-icon> Track orders</li>
        <li><iconify-icon icon="lucide:zap"></iconify-icon> Quick checkout</li>
        <li><iconify-icon icon="lucide:tag"></iconify-icon> Member deals</li>
      </ul>
    </div>
    <div class="jc-auth__tabs">
      <button type="button" class="is-active" data-tab="login">Sign In</button>
      <button type="button" data-tab="register">Create Account</button>
    </div>
    <form id="login-form" class="jc-auth__form">
      <div class="jc-field"><label for="li-email">Email Address</label><input id="li-email" type="email" placeholder="you@example.com" autocomplete="email" required></div>
      <div class="jc-field"><label for="li-pass">Password</label><input id="li-pass" type="password" placeholder="••••••••" autocomplete="current-password" required></div>
      <p class="jc-auth__error" id="login-error"></p>
      <button type="submit" class="jc-btn jc-btn--navy jc-btn--block" id="login-submit">Sign In</button>
    </form>
    <form id="register-form" class="jc-auth__form" hidden>
      <div class="jc-field"><label for="rg-name">Full Name</label><input id="rg-name" type="text" placeholder="e.g. Rajesh Gohil" autocomplete="name" required></div>
      <div class="jc-field"><label for="rg-email">Email Address</label><input id="rg-email" type="email" placeholder="you@example.com" autocomplete="email" required></div>
      <div class="jc-field"><label for="rg-pass">Password <span class="jc-auth__hint">(min. 6 characters)</span></label><input id="rg-pass" type="password" placeholder="••••••••" autocomplete="new-password" required></div>
      <p class="jc-auth__error" id="register-error"></p>
      <button type="submit" class="jc-btn jc-btn--accent jc-btn--block" id="register-submit">Create Account</button>
    </form>
    ${googleClientId ? `<div class="jc-auth__divider"><span>or</span></div><div id="google-signin-host" class="jc-auth__google"></div>` : ''}
    <p class="jc-auth__terms">By continuing you agree to our terms &amp; privacy policy.</p>
  </div>`;

  const loginForm = document.getElementById('login-form');
  const registerForm = document.getElementById('register-form');
  root.querySelectorAll('.jc-auth__tabs button').forEach((btn) => btn.addEventListener('click', () => {
    root.querySelectorAll('.jc-auth__tabs button').forEach((b) => b.classList.toggle('is-active', b === btn));
    const login = btn.dataset.tab === 'login';
    loginForm.hidden = !login;
    registerForm.hidden = login;
  }));

  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = document.getElementById('login-error');
    const btn = document.getElementById('login-submit');
    err.textContent = '';
    btn.disabled = true;
    btn.textContent = 'Signing in…';
    try {
      const user = await authLogin(document.getElementById('li-email').value.trim(), document.getElementById('li-pass').value);
      dashboard(user);
    } catch (ex) {
      err.textContent = (ex && ex.message) || 'Sign in failed.';
      btn.disabled = false;
      btn.textContent = 'Sign In';
    }
  });

  registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = document.getElementById('register-error');
    const btn = document.getElementById('register-submit');
    const pw = document.getElementById('rg-pass').value;
    err.textContent = '';
    if (pw.length < 6) {
      err.textContent = 'Password must be at least 6 characters.';
      return;
    }
    btn.disabled = true;
    btn.textContent = 'Creating account…';
    try {
      const user = await authRegister(
        document.getElementById('rg-email').value.trim(),
        pw,
        document.getElementById('rg-name').value.trim(),
      );
      dashboard(user);
    } catch (ex) {
      err.textContent = (ex && ex.message) || 'Could not create account.';
      btn.disabled = false;
      btn.textContent = 'Create Account';
    }
  });

  initGoogleSignIn(dashboard);
}

function orderCard(o) {
  const tone = statusTone(o.status);
  const itemCount = (o.items || []).length;
  return `<article class="jc-order">
    <div class="jc-order__head">
      <div>
        <span class="jc-order__id">#${esc(o.orderId)}</span>
        <span class="jc-order__date">${esc(o.date || '')}</span>
      </div>
      <span class="jc-order__status jc-order__status--${tone}">${esc(o.status || 'Processing')}</span>
    </div>
    <div class="jc-order__body">
      <span>${itemCount} item${itemCount === 1 ? '' : 's'}</span>
      <span class="jc-order__total">${formatINR(o.total)}</span>
    </div>
    <div class="jc-order__actions">
      <a href="/order-confirmed?id=${encodeURIComponent(o.orderId)}" class="jc-btn jc-btn--ghost jc-btn--sm">View Details</a>
      <button type="button" class="jc-btn jc-btn--navy jc-btn--sm" data-invoice="${esc(o.orderId)}">Download Invoice</button>
    </div>
  </article>`;
}

async function dashboard(user) {
  setProfileDot(true);
  const name = esc(user.displayName || user.email.split('@')[0]);
  const ownerBanner = user.isStaff ? `<div class="jc-account__owner">
    <div><strong>Shop Owner Access</strong><p>Manage products, orders and store settings.</p></div>
    <a href="/admin" class="jc-btn jc-btn--ghost jc-btn--sm">Open Admin Console</a>
  </div>` : '';

  root.innerHTML = `<div class="jc-account__card jc-account__dash">
    <div class="jc-account__profile">
      <div class="jc-account__profile-main">
        <div class="jc-avatar">${esc(initials(user))}</div>
        <div>
          <h2>${name}</h2>
          <p>${esc(user.email)}</p>
        </div>
      </div>
      <button type="button" id="logout-btn" class="jc-account__signout">Sign Out</button>
    </div>
    <div class="jc-account__orders">
      <h3 class="jc-account__h"><iconify-icon icon="lucide:package"></iconify-icon> My Orders</h3>
      <div id="account-orders"><div class="jc-empty"><iconify-icon icon="lucide:loader-2" class="jc-spin"></iconify-icon><p>Loading orders…</p></div></div>
      ${ownerBanner}
    </div>
  </div>`;

  document.getElementById('logout-btn').addEventListener('click', async () => {
    await authLogout();
    authView();
  });

  const box = document.getElementById('account-orders');
  try {
    const orders = await getMyOrders();
    orders.sort((a, b) => String(b.orderId).localeCompare(String(a.orderId)));
    if (!orders.length) {
      box.innerHTML = `<div class="jc-empty jc-empty--dashed">
        <iconify-icon icon="lucide:shopping-bag"></iconify-icon>
        <p><strong>No orders found</strong></p>
        <p class="jc-empty__sub">Place your first order and it will appear here. Make sure to checkout using <strong>${esc(user.email)}</strong>.</p>
        <a href="/shop" class="jc-btn jc-btn--navy">Start Shopping</a>
      </div>`;
      return;
    }
    box.innerHTML = `<div class="jc-orders">${orders.map(orderCard).join('')}</div>`;
    box.querySelectorAll('[data-invoice]').forEach((btn) => btn.addEventListener('click', () => {
      sessionStorage.setItem('jc-print-invoice', '1');
      location.href = `/order-confirmed?id=${encodeURIComponent(btn.dataset.invoice)}`;
    }));
  } catch {
    box.innerHTML = '<div class="jc-empty"><p>Unable to load your orders right now.</p></div>';
  }
}

(async function init() {
  try {
    const user = await authMe();
    if (user) dashboard(user);
    else authView();
  } catch {
    authView();
  }
})();
