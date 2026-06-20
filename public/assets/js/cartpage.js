/* Cart page — render items, quantity/remove, totals, promo. */
import { getCart, setQty, removeFromCart, cartCount, computeTotals } from './cart.js';
import { formatINR } from './api.js';
import { esc } from './products.js';

const itemsEl = document.getElementById('cart-items');
const grid = document.getElementById('cart-grid');
const emptyEl = document.getElementById('cart-empty');
const countLabel = document.getElementById('cart-count-label');
const subtotalEl = document.getElementById('cart-subtotal');
const gstEl = document.getElementById('cart-gst');
const totalEl = document.getElementById('cart-total');
const proceedBtn = document.getElementById('proceed-checkout-btn');
const promoStatus = document.getElementById('cart-promo-status');

const PROMO_KEY = 'jc-cart-promo-discount';
let discount = Number(sessionStorage.getItem(PROMO_KEY)) || 0;

function itemHTML(it) {
  const media = it.imageUrl
    ? `<img src="${esc(it.imageUrl)}" alt="${esc(it.name)}">`
    : `<iconify-icon icon="${esc(it.imageIcon || 'lucide:box')}"></iconify-icon>`;
  return `<div class="jc-cart-item" data-id="${esc(it.id)}">
    <div class="jc-cart-item__media">${media}</div>
    <div class="jc-cart-item__body">
      <div class="jc-cart-item__top">
        <div>
          <p class="jc-cart-item__brand">${esc(it.brand || '')}</p>
          <h3 class="jc-cart-item__name"><a href="/product?id=${encodeURIComponent(it.id)}">${esc(it.name)}</a></h3>
          ${it.details ? `<p class="jc-cart-item__details">${esc(it.details)}</p>` : ''}
        </div>
        <button type="button" class="jc-cart-item__remove" data-remove aria-label="Remove item"><iconify-icon icon="lucide:x"></iconify-icon></button>
      </div>
      <div class="jc-cart-item__bottom">
        <div class="jc-qty">
          <button type="button" data-dec aria-label="Decrease"><iconify-icon icon="lucide:minus"></iconify-icon></button>
          <input type="number" value="${it.quantity}" min="1" data-qty aria-label="Quantity">
          <button type="button" data-inc aria-label="Increase"><iconify-icon icon="lucide:plus"></iconify-icon></button>
        </div>
        <div class="jc-cart-item__price">
          <span class="l">Subtotal</span>
          <span class="v">${formatINR(it.price * it.quantity)}</span>
        </div>
      </div>
    </div>
  </div>`;
}

function renderTotals() {
  const t = computeTotals({ discount });
  subtotalEl.textContent = formatINR(t.subtotal);
  gstEl.textContent = formatINR(t.gst);
  totalEl.textContent = formatINR(t.total);
}

function render() {
  const cart = getCart();
  const n = cartCount();
  countLabel.textContent = `You have ${n} item${n === 1 ? '' : 's'} in your bag`;
  if (!cart.length) {
    grid.style.display = 'none';
    emptyEl.style.display = 'flex';
    discount = 0;
    sessionStorage.removeItem(PROMO_KEY);
    return;
  }
  grid.style.display = '';
  emptyEl.style.display = 'none';
  itemsEl.innerHTML = cart.map(itemHTML).join('');
  renderTotals();

  itemsEl.querySelectorAll('.jc-cart-item').forEach((row) => {
    const id = row.dataset.id;
    const input = row.querySelector('[data-qty]');
    const sync = (q) => { setQty(id, q); render(); };
    row.querySelector('[data-dec]').addEventListener('click', () => sync(Math.max(1, (parseInt(input.value, 10) || 1) - 1)));
    row.querySelector('[data-inc]').addEventListener('click', () => sync((parseInt(input.value, 10) || 1) + 1));
    input.addEventListener('change', () => sync(Math.max(1, parseInt(input.value, 10) || 1)));
    row.querySelector('[data-remove]').addEventListener('click', () => { removeFromCart(id); render(); });
  });
}

/* Promo — data-driven: matches a code on any product in the cart. */
document.getElementById('cart-promo-apply').addEventListener('click', () => {
  const code = (document.getElementById('cart-promo-input').value || '').trim().toUpperCase();
  promoStatus.className = 'jc-summary__promo-status';
  if (!code) return;
  const cart = getCart();
  let d = 0;
  cart.forEach((it) => {
    if (it.promoCode && it.promoCode.toUpperCase() === code && it.promoDiscount) {
      d += Math.round(it.price * it.quantity * (it.promoDiscount / 100));
    }
  });
  if (d > 0) {
    discount = d;
    sessionStorage.setItem(PROMO_KEY, String(d));
    promoStatus.textContent = `Code applied — you saved ${formatINR(d)}.`;
    promoStatus.classList.add('is-ok');
  } else {
    discount = 0;
    sessionStorage.removeItem(PROMO_KEY);
    promoStatus.textContent = 'This code is not valid for the items in your cart.';
    promoStatus.classList.add('is-err');
  }
  renderTotals();
});

if (discount > 0) {
  promoStatus.textContent = `Promo applied — you saved ${formatINR(discount)}.`;
  promoStatus.classList.add('is-ok');
}

window.addEventListener('cart:change', render);
render();
