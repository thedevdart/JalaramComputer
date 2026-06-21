/* Jalaram Computers — JSON API client.
   Thin wrapper over the Django endpoints in shop/api_views.py. */

function csrfToken() {
  const m = document.cookie.match(/csrftoken=([^;]+)/);
  return m ? decodeURIComponent(m[1]) : '';
}

export async function apiFetch(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' };
  if (method !== 'GET' && method !== 'HEAD') headers['X-CSRFToken'] = csrfToken();
  const res = await fetch(path, {
    method,
    credentials: 'same-origin',
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let data = null;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) {
    const err = new Error((data && data.error) || res.statusText || 'Request failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

/* ── Catalog ── */
export const getProducts = () => apiFetch('/api/products/');
export const getProduct = (id) => apiFetch(`/api/products/${encodeURIComponent(id)}/`);
export const getShopSettings = () => apiFetch('/api/settings/shop/');
export const getHeroSlides = () => apiFetch('/api/settings/hero-slides/');

/* ── Orders ── */
export const saveOrder = (order) => apiFetch('/api/orders/', { method: 'POST', body: order });
export const getMyOrders = () => apiFetch('/api/orders/');
export const getOrder = (id) => apiFetch(`/api/orders/${encodeURIComponent(id)}/`);

/* ── Forms ── */
export const saveContactQuery = (payload) => apiFetch('/api/queries/', { method: 'POST', body: payload });
export const saveServiceBooking = (payload) => apiFetch('/api/service-bookings/', { method: 'POST', body: payload });
export const subscribeNewsletter = (email) => apiFetch('/api/newsletter/subscribe/', { method: 'POST', body: { email } });

/* ── Auth ── */
export const authMe = () => apiFetch('/api/auth/me/').then((d) => (d && d.user) || null);
export const authLogin = (email, password) => apiFetch('/api/auth/login/', { method: 'POST', body: { email, password } }).then((d) => d.user);
export const authRegister = (email, password, fullName) => apiFetch('/api/auth/register/', { method: 'POST', body: { email, password, fullName } }).then((d) => d.user);
export const authLogout = () => apiFetch('/api/auth/logout/', { method: 'POST', body: {} });
export const authGoogle = (credential) =>
  apiFetch('/api/auth/google/', { method: 'POST', body: { credential } }).then((d) => d.user);
export const getAuthConfig = () => apiFetch('/api/auth/config/');

/* ── Formatting helpers ── */
export const formatINR = (n) =>
  '₹' + Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 0 });
