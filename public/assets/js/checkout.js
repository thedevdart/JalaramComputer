/* Checkout — order summary, delivery/shipping, place order via API. */
import { getCart, computeTotals, clearCart, cartCount } from './cart.js';
import { formatINR, saveOrder } from './api.js';
import { esc } from './products.js';

const itemsEl = document.getElementById('checkout-items');
const subtotalEl = document.getElementById('co-subtotal');
const shippingEl = document.getElementById('co-shipping');
const gstEl = document.getElementById('co-gst');
const totalEl = document.getElementById('co-total');
const errorEl = document.getElementById('checkout-error');
const placeBtn = document.getElementById('place-order-btn');

function shipping() {
  const sel = document.querySelector('input[name="delivery"]:checked');
  return sel ? Number(sel.value) : 0;
}
function deliveryLabel() {
  const sel = document.querySelector('input[name="delivery"]:checked');
  return sel ? sel.dataset.label : 'Standard';
}
function payment() {
  const sel = document.querySelector('input[name="payment"]:checked');
  return sel ? sel.value : 'gateway';
}

function renderItems() {
  const cart = getCart();
  itemsEl.innerHTML = cart.map((it) => `<div class="jc-checkout__item">
    <div class="jc-checkout__item-media"><iconify-icon icon="${esc(it.imageIcon || 'lucide:box')}"></iconify-icon></div>
    <div class="jc-checkout__item-body"><h4>${esc(it.name)}</h4><p>Quantity: ${it.quantity}</p></div>
    <span class="jc-checkout__item-price">${formatINR(it.price * it.quantity)}</span>
  </div>`).join('');
}

function renderTotals() {
  const ship = shipping();
  const t = computeTotals({ shipping: ship });
  subtotalEl.textContent = formatINR(t.subtotal);
  shippingEl.textContent = ship ? formatINR(ship) : 'Free';
  gstEl.textContent = formatINR(t.gst);
  totalEl.textContent = formatINR(t.total);
}

function validate(data) {
  if (!data.name) return 'Please enter your full name.';
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) return 'Please enter a valid email address.';
  if (!/^[0-9+\-\s]{7,15}$/.test(data.phone)) return 'Please enter a valid phone number.';
  if (!/^[1-9][0-9]{5}$/.test(data.pincode)) return 'Please enter a valid 6-digit pincode.';
  if (!data.address) return 'Please enter your address.';
  if (!data.city || !data.state) return 'Please enter your city and state.';
  return null;
}

async function placeOrder() {
  errorEl.textContent = '';
  const form = document.getElementById('checkout-form');
  const fd = new FormData(form);
  const data = Object.fromEntries([...fd.entries()].map(([k, v]) => [k, String(v).trim()]));
  const err = validate(data);
  if (err) { errorEl.textContent = err; errorEl.scrollIntoView({ behavior: 'smooth', block: 'center' }); return; }

  const cart = getCart();
  if (!cart.length) return;
  const ship = shipping();
  const t = computeTotals({ shipping: ship });

  const order = {
    date: new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' }),
    status: 'Processing',
    paid: payment() === 'gateway',
    subtotal: t.subtotal, discount: 0, gst: t.gst, total: t.total,
    customer: { name: data.name, email: data.email, phone: data.phone },
    shippingDetails: {
      address: data.address, city: data.city, state: data.state,
      pincode: data.pincode, gst: data.gst || '', method: deliveryLabel(),
    },
    items: cart,
    paymentMethod: payment() === 'gateway' ? 'Secure Payment Gateway' : 'Cash on Delivery',
  };

  placeBtn.disabled = true;
  placeBtn.textContent = 'Processing…';
  try {
    const res = await saveOrder(order);
    const orderId = (res && res.order && res.order.orderId) || '';
    sessionStorage.setItem('jc-last-order', orderId);
    clearCart();
    location.href = `/order-confirmed?id=${encodeURIComponent(orderId)}`;
  } catch (e) {
    errorEl.textContent = (e && e.message) || 'Could not place your order. Please try again.';
    placeBtn.disabled = false;
    placeBtn.innerHTML = 'Complete Payment <iconify-icon icon="lucide:shield-check"></iconify-icon>';
  }
}

function init() {
  if (!cartCount()) {
    document.querySelector('.jc-checkout__grid').style.display = 'none';
    document.querySelector('.jc-steps').style.display = 'none';
    document.getElementById('checkout-empty').style.display = 'flex';
    return;
  }
  renderItems();
  renderTotals();
  document.querySelectorAll('input[name="delivery"]').forEach((r) => r.addEventListener('change', renderTotals));
  placeBtn.addEventListener('click', placeOrder);
}
init();
