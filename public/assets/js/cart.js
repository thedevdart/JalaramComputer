/* Jalaram Computers — cart state.
   Persists to localStorage ('cart_items') and keeps the header badge in sync. */

const KEY = 'cart_items';

export function getCart() {
  try { return JSON.parse(localStorage.getItem(KEY)) || []; }
  catch { return []; }
}

function save(items) {
  localStorage.setItem(KEY, JSON.stringify(items));
  updateBadge();
  window.dispatchEvent(new CustomEvent('cart:change', { detail: items }));
}

export function addToCart(product, qty = 1) {
  const items = getCart();
  const existing = items.find((i) => i.id === product.id);
  if (existing) {
    existing.quantity += qty;
  } else {
    items.push({
      id: product.id,
      name: product.name,
      brand: product.brand || '',
      details: product.details || '',
      price: Number(product.price) || 0,
      imageIcon: product.imageIcon || 'lucide:box',
      imageUrl: product.imageUrl || '',
      promoCode: product.promoCode || '',
      promoDiscount: Number(product.promoDiscount) || 0,
      quantity: qty,
    });
  }
  save(items);
  showToast(`${product.name} added to cart`);
}

export function removeFromCart(id) { save(getCart().filter((i) => i.id !== id)); }

export function setQty(id, qty) {
  const items = getCart();
  const item = items.find((i) => i.id === id);
  if (!item) return;
  item.quantity = Math.max(1, qty);
  save(items);
}

export function clearCart() { save([]); }

export const cartCount = () => getCart().reduce((n, i) => n + i.quantity, 0);
export const cartSubtotal = () => getCart().reduce((s, i) => s + i.price * i.quantity, 0);

export const GST_RATE = 0.18;

/** Compute order totals. `shipping` and `discount` are absolute rupee amounts. */
export function computeTotals({ shipping = 0, discount = 0 } = {}) {
  const subtotal = cartSubtotal();
  const taxable = Math.max(0, subtotal - discount);
  const gst = Math.round(taxable * GST_RATE);
  const total = taxable + shipping + gst;
  return { subtotal, discount, shipping, gst, total };
}

function updateBadge() {
  const n = cartCount();
  document.querySelectorAll('[data-cart-count]').forEach((el) => {
    el.textContent = n;
    el.toggleAttribute('data-empty', n === 0);
  });
}

/* Lightweight toast (self-contained, no CSS dependency) */
let toastTimer;
export function showToast(message) {
  let el = document.getElementById('jc-toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'jc-toast';
    el.style.cssText =
      'position:fixed;left:50%;bottom:5.5rem;transform:translateX(-50%) translateY(1rem);' +
      'z-index:9000;background:#091A2E;color:#fff;font:600 0.8rem/1.4 Inter,sans-serif;' +
      'letter-spacing:0.02em;padding:0.75rem 1.25rem;border:1px solid rgba(212,175,55,0.4);' +
      'border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,0.3);opacity:0;' +
      'transition:opacity .25s ease,transform .25s ease;pointer-events:none;max-width:90vw;';
    document.body.appendChild(el);
  }
  el.textContent = message;
  requestAnimationFrame(() => { el.style.opacity = '1'; el.style.transform = 'translateX(-50%) translateY(0)'; });
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.style.opacity = '0';
    el.style.transform = 'translateX(-50%) translateY(1rem)';
  }, 2200);
}

updateBadge();
window.addEventListener('storage', (e) => { if (e.key === KEY) updateBadge(); });
