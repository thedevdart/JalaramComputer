/* Shared product-card rendering + wiring (home featured grid + shop). */
import { addToCart } from './cart.js';
import { formatINR } from './api.js';

export function esc(s) {
  return String(s == null ? '' : s)
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function starsHTML(rating, count) {
  const r = Math.round(Number(rating) || 0);
  let out = '';
  for (let i = 1; i <= 5; i++) {
    out += `<iconify-icon icon="lucide:star" class="${i <= r ? 'star-gold' : 'star-off'}"></iconify-icon>`;
  }
  if (count) out += `<span>(${count})</span>`;
  return out;
}

const BADGE_TONE = { hot: 'gold', new: 'gold', featured: 'gold', bestseller: 'navy', sale: 'charcoal' };

export function productCardHTML(p) {
  const price = Number(p.price) || 0;
  const orig = Number(p.originalPrice) || 0;
  const hasDiscount = orig > price;
  const tone = BADGE_TONE[(p.badge || '').toLowerCase()] || (hasDiscount ? 'charcoal' : 'navy');
  const badge = p.badge
    ? `<span class="product-card__badge product-card__badge--${tone}">${esc(p.badge)}</span>`
    : (hasDiscount ? `<span class="product-card__badge product-card__badge--charcoal">-${Math.round((1 - price / orig) * 100)}%</span>` : '');
  const media = p.imageUrl
    ? `<img src="${esc(p.imageUrl)}" alt="${esc(p.name)}" loading="lazy">`
    : `<iconify-icon icon="${esc(p.imageIcon || 'lucide:box')}"></iconify-icon>`;
  return `<article class="product-card" data-id="${esc(p.id)}">
    <div class="product-card__media">${media}${badge}
      <div class="product-card__quick">
        <button type="button" data-view aria-label="Quick view"><iconify-icon icon="lucide:eye"></iconify-icon></button>
        <button type="button" aria-label="Wishlist"><iconify-icon icon="lucide:heart"></iconify-icon></button>
        <button type="button" aria-label="Compare"><iconify-icon icon="lucide:shuffle"></iconify-icon></button>
      </div>
    </div>
    <div class="product-card__body">
      <p class="product-card__brand">${esc(p.brand || '')}</p>
      <h3 class="product-card__name">${esc(p.name)}</h3>
      <div class="product-card__stars">${starsHTML(p.rating, p.ratingCount)}</div>
      <div class="product-card__price"><b>${formatINR(price)}</b>${hasDiscount ? `<s>${formatINR(orig)}</s>` : ''}</div>
      <button type="button" class="product-card__cta" data-add><iconify-icon icon="lucide:shopping-bag"></iconify-icon> Add to Cart</button>
    </div>
  </article>`;
}

/** Render products into a container and wire interactions. `products` is the
    full list; cards link to /product?id=… and add to cart. */
export function renderProducts(container, products) {
  if (!container) return;
  container.innerHTML = products.map(productCardHTML).join('');
  const byId = Object.fromEntries(products.map((p) => [p.id, p]));

  container.querySelectorAll('.product-card').forEach((card) => {
    const id = card.dataset.id;
    const go = () => { window.location.href = `/product?id=${encodeURIComponent(id)}`; };
    card.addEventListener('click', (e) => {
      if (e.target.closest('[data-add]') || e.target.closest('[data-view]')) return;
      go();
    });
    const view = card.querySelector('[data-view]');
    if (view) view.addEventListener('click', go);
    const add = card.querySelector('[data-add]');
    if (add) add.addEventListener('click', (e) => { e.stopPropagation(); addToCart(byId[id]); });
  });
}
