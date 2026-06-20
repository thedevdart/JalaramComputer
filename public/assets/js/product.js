/* Product detail — loads ?id=…, renders gallery/info/specs/overview + recommended. */
import { getProduct, getProducts, formatINR } from './api.js';
import { addToCart } from './cart.js';
import { renderProducts, esc } from './products.js';

const root = document.getElementById('product-root');
const id = new URLSearchParams(location.search).get('id');
const SPEC_ICONS = ['lucide:cpu', 'lucide:monitor', 'lucide:database', 'lucide:hard-drive', 'lucide:zap', 'lucide:settings'];

function stars(rating) {
  const r = Math.round(Number(rating) || 0);
  let out = '';
  for (let i = 1; i <= 5; i++) out += `<iconify-icon icon="lucide:star" class="${i <= r ? 'star-gold' : 'star-off'}"></iconify-icon>`;
  return out;
}

function galleryHTML(p) {
  const imgs = (p.images && p.images.length ? p.images : [p.imageUrl, p.imageUrl2, p.imageUrl3, p.imageUrl4]).filter(Boolean);
  const main = imgs[0]
    ? `<img id="pd-main" src="${esc(imgs[0])}" alt="${esc(p.name)}">`
    : `<iconify-icon icon="${esc(p.imageIcon || 'lucide:box')}"></iconify-icon>`;
  const badge = p.badge ? `<span class="product-card__badge product-card__badge--gold">${esc(p.badge)}</span>` : '';
  const thumbs = imgs.length > 1
    ? `<div class="jc-product__thumbs">${imgs.slice(0, 4).map((src, i) =>
        `<div class="jc-product__thumb${i === 0 ? ' is-active' : ''}" data-src="${esc(src)}"><img src="${esc(src)}" alt=""></div>`).join('')}</div>`
    : '';
  return `<div class="jc-product__gallery"><div class="jc-product__stage">${main}${badge}</div>${thumbs}</div>`;
}

function specsHTML(p) {
  const parts = String(p.details || '').split(/[|,•·]/).map((s) => s.trim()).filter(Boolean).slice(0, 4);
  if (!parts.length) return '';
  return `<div class="jc-product__specs">${parts.map((part, i) => {
    const [k, ...rest] = part.split(':');
    const hasKey = rest.length > 0;
    return `<div class="jc-product__spec"><iconify-icon icon="${SPEC_ICONS[i % SPEC_ICONS.length]}"></iconify-icon>
      <div><p class="k">${hasKey ? esc(k) : 'Feature'}</p><p class="v">${esc(hasKey ? rest.join(':').trim() : part)}</p></div></div>`;
  }).join('')}</div>`;
}

function render(p, all) {
  const price = Number(p.price) || 0;
  const orig = Number(p.originalPrice) || 0;
  const save = orig > price ? Math.round((1 - price / orig) * 100) : 0;
  const inStock = (p.stock || 0) > 0;

  root.innerHTML = `<div class="jc-product">
    <nav class="jc-breadcrumb" style="color:var(--muted)">
      <a href="/">Home</a><span>/</span><a href="/shop">Shop</a><span>/</span>
      <a href="/shop?category=${encodeURIComponent(p.category || '')}">${esc(p.category || 'Products')}</a><span>/</span>
      <span style="color:var(--navy)">${esc(p.name)}</span>
    </nav>

    <div class="jc-product__top">
      ${galleryHTML(p)}
      <div class="jc-product__info">
        <div class="jc-product__meta"><span class="brand">${esc(p.brand || '')}</span><span class="sku">SKU: ${esc((p.id || '').toUpperCase())}</span></div>
        <h1 class="jc-product__name">${esc(p.name)}</h1>
        <div class="jc-product__rating">
          <span class="stars">${stars(p.rating)}</span>
          <span>(${p.ratingCount || 0} Reviews)</span>
          <span class="jc-product__stock${inStock ? '' : ' is-out'}"><span class="dot"></span>${inStock ? 'In Stock' : 'Out of Stock'}</span>
        </div>
        <div class="jc-product__price">
          <span class="now">${formatINR(price)}</span>
          ${save ? `<span class="was">${formatINR(orig)}</span><span class="save">Save ${save}%</span>` : ''}
        </div>
        ${specsHTML(p)}
        <div class="jc-product__actions">
          <div class="jc-qty">
            <button type="button" id="qty-dec" aria-label="Decrease"><iconify-icon icon="lucide:minus"></iconify-icon></button>
            <input type="number" id="qty-input" value="1" min="1" aria-label="Quantity">
            <button type="button" id="qty-inc" aria-label="Increase"><iconify-icon icon="lucide:plus"></iconify-icon></button>
          </div>
          <button type="button" id="pd-add" class="jc-btn jc-btn--navy jc-product__add"${inStock ? '' : ' disabled'}>
            <iconify-icon icon="lucide:shopping-bag"></iconify-icon> Add to Shopping Bag</button>
          <button type="button" class="jc-product__wish" aria-label="Wishlist"><iconify-icon icon="lucide:heart"></iconify-icon></button>
        </div>
        <div class="jc-product__assurance">
          <div><iconify-icon icon="lucide:shield-check"></iconify-icon><div><p class="t">1-Year On-Site Warranty</p><p class="d">Coverage for hardware failures with priority doorstep service within 24 hours.</p></div></div>
          <div><iconify-icon icon="lucide:refresh-cw"></iconify-icon><div><p class="t">7-Day Seamless Return</p><p class="d">Change your mind? No-questions-asked return policy for sealed products.</p></div></div>
        </div>
      </div>
    </div>

    ${p.details ? `<div class="jc-product__overview"><h2>Product <em style="color:var(--navy);font-style:italic">Overview</em></h2><p>${esc(p.details)}</p></div>` : ''}

    <div class="jc-recommended">
      <div class="jc-head"><div><span class="jc-kicker">Complementary Gear</span><h2 class="jc-title">You Might <em>Also Like</em></h2></div>
        <a href="/shop" class="jc-link">Explore Collection <iconify-icon icon="lucide:arrow-right"></iconify-icon></a></div>
      <div id="pd-recommended" class="jc-products"></div>
    </div>
  </div>`;

  // Gallery thumbnails
  const main = document.getElementById('pd-main');
  root.querySelectorAll('.jc-product__thumb').forEach((t) => t.addEventListener('click', () => {
    if (main) main.src = t.dataset.src;
    root.querySelectorAll('.jc-product__thumb').forEach((x) => x.classList.toggle('is-active', x === t));
  }));

  // Quantity + add to cart
  const qtyInput = document.getElementById('qty-input');
  const qty = () => Math.max(1, parseInt(qtyInput.value, 10) || 1);
  document.getElementById('qty-dec').addEventListener('click', () => { qtyInput.value = Math.max(1, qty() - 1); });
  document.getElementById('qty-inc').addEventListener('click', () => { qtyInput.value = qty() + 1; });
  const addBtn = document.getElementById('pd-add');
  if (inStock) addBtn.addEventListener('click', () => addToCart(p, qty()));

  // Recommended
  const rec = all.filter((x) => x.id !== p.id).sort(() => Math.random() - 0.5).slice(0, 4);
  if (rec.length) renderProducts(document.getElementById('pd-recommended'), rec);
  else document.getElementById('pd-recommended').innerHTML = '<div class="jc-empty jc-empty--span"><p>More products coming soon.</p></div>';

  document.title = `${p.name} — Jalaram Computers`;
}

(async function init() {
  if (!id) { location.href = '/shop'; return; }
  try {
    const [p, all] = await Promise.all([getProduct(id), getProducts().catch(() => [])]);
    render(p, all);
  } catch {
    root.innerHTML = `<div class="jc-product"><div class="jc-empty jc-empty--span" style="min-height:40vh">
      <iconify-icon icon="lucide:package-x"></iconify-icon>
      <p>This product could not be found.</p><a href="/shop" class="jc-btn jc-btn--navy">Back to Shop</a></div></div>`;
  }
})();
