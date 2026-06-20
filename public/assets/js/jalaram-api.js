/**
 * Jalaram Computers — Django REST API client (replaces Firebase).
 */

const API_BASE = '';

function getCsrfToken() {
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

async function apiFetch(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };
  const method = (options.method || 'GET').toUpperCase();
  if (method !== 'GET' && method !== 'HEAD') {
    headers['X-CSRFToken'] = getCsrfToken();
  }
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: 'same-origin',
    ...options,
    headers,
  });
  const text = await res.text();
  let data = null;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }
  if (!res.ok) {
    const err = new Error(data?.error || res.statusText || 'Request failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }
  return data;
}

/** Connected backend marker (truthy when API is reachable). */
export let db = null;

const productListeners = new Set();
let productsPollTimer = null;

function notifyProductListeners(products) {
  productListeners.forEach((cb) => {
    try {
      cb({ docs: products.map((p) => ({ data: () => p, id: p.id })) });
    } catch (e) {
      console.warn('Product listener error:', e);
    }
  });
}

export function onProductsSnapshot(callback) {
  productListeners.add(callback);
  return () => productListeners.delete(callback);
}

async function pollProducts() {
  try {
    const products = await apiFetch('/api/products/');
    notifyProductListeners(products);
    db = { connected: true };
  } catch (e) {
    console.warn('Products poll error:', e);
  }
}

export function startProductsPolling(intervalMs = 15000) {
  pollProducts();
  if (productsPollTimer) clearInterval(productsPollTimer);
  productsPollTimer = setInterval(pollProducts, intervalMs);
}

export async function fetchShopSettings() {
  return apiFetch('/api/settings/shop/');
}

export async function fetchHeroSlides() {
  return apiFetch('/api/settings/hero-slides/');
}

export async function saveOrder(orderDetails) {
  return apiFetch('/api/orders/', {
    method: 'POST',
    body: JSON.stringify(orderDetails),
  });
}

export async function fetchMyOrders() {
  return apiFetch('/api/orders/');
}

export async function saveContactQuery(payload) {
  return apiFetch('/api/queries/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function saveServiceBooking(payload) {
  return apiFetch('/api/service-bookings/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function authMe() {
  const data = await apiFetch('/api/auth/me/');
  return data?.user || null;
}

export async function authRegister(email, password, fullName) {
  const data = await apiFetch('/api/auth/register/', {
    method: 'POST',
    body: JSON.stringify({ email, password, fullName }),
  });
  return data.user;
}

export async function authLogin(email, password) {
  const data = await apiFetch('/api/auth/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  return data.user;
}

export async function authLogout() {
  return apiFetch('/api/auth/logout/', { method: 'POST', body: '{}' });
}

export async function adminLogin(username, password) {
  const data = await apiFetch('/api/auth/admin-login/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  return data;
}

export async function adminSaveProduct(product) {
  return apiFetch(`/api/products/${encodeURIComponent(product.id)}/`, {
    method: 'POST',
    body: JSON.stringify(product),
  });
}

export async function adminDeleteProduct(id) {
  return apiFetch(`/api/products/${encodeURIComponent(id)}/`, {
    method: 'DELETE',
  });
}

export async function adminSaveShopSettings(settings) {
  return apiFetch('/api/settings/shop/admin/', {
    method: 'PUT',
    body: JSON.stringify(settings),
  });
}

export async function adminSaveOrder(order) {
  return apiFetch(`/api/orders/${encodeURIComponent(order.orderId)}/`, {
    method: 'PUT',
    body: JSON.stringify(order),
  });
}

export async function adminFetchOrders() {
  return apiFetch('/api/orders/');
}

export async function adminFetchProducts() {
  return apiFetch('/api/products/');
}

export async function adminSaveService(service) {
  return apiFetch('/api/services/', {
    method: 'POST',
    body: JSON.stringify(service),
  });
}

export async function adminFetchServices() {
  return apiFetch('/api/services/');
}

export async function adminBulkSync(payload) {
  return apiFetch('/api/admin/sync/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function adminClearProducts() {
  return apiFetch('/api/admin/clear-products/', { method: 'POST', body: '{}' });
}

export async function initBackend() {
  db = { connected: true };
  startProductsPolling(15000);
  try {
    await pollProducts();
  } catch (e) {
    db = null;
    throw e;
  }
  return db;
}

const authListeners = new Set();

export function onAuthStateChanged(callback) {
  authListeners.add(callback);
  authMe().then((user) => callback(user)).catch(() => callback(null));
  return () => authListeners.delete(callback);
}

export function notifyAuthChange(user) {
  authListeners.forEach((cb) => {
    try {
      cb(user);
    } catch (e) {
      console.warn('Auth listener error:', e);
    }
  });
}

export async function loginWithEmailApi(email, password) {
  const user = await authLogin(email, password);
  notifyAuthChange(user);
  return user;
}

export async function registerWithEmailApi(email, password, fullName) {
  const user = await authRegister(email, password, fullName);
  notifyAuthChange(user);
  return user;
}

export async function logoutApi() {
  await authLogout();
  notifyAuthChange(null);
}
