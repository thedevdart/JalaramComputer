/* Shop — filters (category, price, brand, rating), sort, search, live grid. */
import { getProducts, formatINR } from './api.js';
import { renderProducts, esc } from './products.js';

const grid = document.getElementById('products-grid');
const showingCount = document.getElementById('showing-count');
const totalCount = document.getElementById('total-count');
const sortSelect = document.getElementById('sort-select');
const priceSlider = document.getElementById('price-slider');
const priceLabel = document.getElementById('price-label');

const params = new URLSearchParams(location.search);
const state = {
  query: (params.get('q') || '').trim().toLowerCase(),
  category: params.get('category') || 'All',
  brands: new Set(),
  minRating: 0,
  maxPrice: 200000,
  sort: 'featured',
};

let ALL = [];

function uniqueSorted(values) {
  return [...new Set(values.filter(Boolean))].sort((a, b) => a.localeCompare(b));
}

function buildCategoryFilter() {
  const cats = ['All', ...uniqueSorted(ALL.map((p) => p.category))];
  const counts = (c) => (c === 'All' ? ALL.length : ALL.filter((p) => p.category === c).length);
  const ul = document.getElementById('filter-categories');
  ul.innerHTML = cats.map((c) =>
    `<li><button type="button" class="jc-filter__cat${c === state.category ? ' is-active' : ''}" data-category="${esc(c)}">
       <span>${c === 'All' ? 'All Categories' : esc(c)}</span><span class="jc-filter__count">${counts(c)}</span></button></li>`).join('');
  ul.querySelectorAll('.jc-filter__cat').forEach((btn) => btn.addEventListener('click', () => {
    state.category = btn.dataset.category;
    ul.querySelectorAll('.jc-filter__cat').forEach((b) => b.classList.toggle('is-active', b === btn));
    apply();
  }));
}

function buildBrandFilter() {
  const brands = uniqueSorted(ALL.map((p) => p.brand));
  const box = document.getElementById('filter-brands');
  box.innerHTML = brands.map((b) =>
    `<label class="jc-check"><input type="checkbox" value="${esc(b)}"><span>${esc(b)}</span></label>`).join('') ||
    '<p class="jc-filter__none">No brands yet.</p>';
  box.querySelectorAll('input').forEach((cb) => cb.addEventListener('change', () => {
    cb.checked ? state.brands.add(cb.value) : state.brands.delete(cb.value);
    apply();
  }));
}

function initPrice() {
  const max = Math.max(1000, ...ALL.map((p) => Number(p.price) || 0));
  priceSlider.max = Math.ceil(max / 500) * 500;
  priceSlider.value = priceSlider.max;
  state.maxPrice = Number(priceSlider.value);
  priceLabel.textContent = formatINR(priceSlider.value);
  priceSlider.addEventListener('input', () => {
    state.maxPrice = Number(priceSlider.value);
    priceLabel.textContent = formatINR(priceSlider.value);
    apply();
  });
}

function sortList(list) {
  const s = state.sort;
  const arr = list.slice();
  if (s === 'price-asc') arr.sort((a, b) => a.price - b.price);
  else if (s === 'price-desc') arr.sort((a, b) => b.price - a.price);
  else if (s === 'rating') arr.sort((a, b) => (b.rating || 0) - (a.rating || 0));
  else if (s === 'newest') arr.sort((a, b) => (b.createdAt || 0) - (a.createdAt || 0));
  return arr;
}

function apply() {
  let list = ALL.filter((p) => {
    if (state.category !== 'All' && p.category !== state.category) return false;
    if (state.brands.size && !state.brands.has(p.brand)) return false;
    if ((p.rating || 0) < state.minRating) return false;
    if ((Number(p.price) || 0) > state.maxPrice) return false;
    if (state.query) {
      const hay = `${p.name} ${p.brand} ${p.category} ${p.details}`.toLowerCase();
      if (!hay.includes(state.query)) return false;
    }
    return true;
  });
  list = sortList(list);
  showingCount.textContent = list.length;
  totalCount.textContent = ALL.length;
  if (!list.length) {
    grid.innerHTML = `<div class="jc-empty jc-empty--span"><iconify-icon icon="lucide:search-x"></iconify-icon>
      <p>No products match your filters${state.query ? ` for “${esc(state.query)}”` : ''}.</p></div>`;
    return;
  }
  renderProducts(grid, list);
}

function initRating() {
  document.querySelectorAll('#filter-rating button').forEach((btn) => btn.addEventListener('click', () => {
    const r = Number(btn.dataset.rating);
    const active = btn.classList.contains('is-active');
    document.querySelectorAll('#filter-rating button').forEach((b) => b.classList.remove('is-active'));
    state.minRating = active ? 0 : r;
    if (!active) btn.classList.add('is-active');
    apply();
  }));
}

function initClear() {
  document.getElementById('clear-filters-btn').addEventListener('click', () => {
    state.category = 'All'; state.brands.clear(); state.minRating = 0; state.query = '';
    state.maxPrice = Number(priceSlider.max); priceSlider.value = priceSlider.max;
    priceLabel.textContent = formatINR(priceSlider.max);
    document.querySelectorAll('#filter-brands input').forEach((cb) => (cb.checked = false));
    document.querySelectorAll('#filter-rating button').forEach((b) => b.classList.remove('is-active'));
    buildCategoryFilter();
    apply();
  });
}

function initToggle() {
  const btn = document.getElementById('filter-toggle');
  const filters = document.getElementById('shop-filters');
  if (btn) btn.addEventListener('click', () => filters.classList.toggle('is-open'));
}

sortSelect.addEventListener('change', () => { state.sort = sortSelect.value; apply(); });

(async function init() {
  try {
    ALL = await getProducts();
  } catch {
    grid.innerHTML = '<div class="jc-empty jc-empty--span"><p>Unable to load products right now.</p></div>';
    return;
  }
  buildCategoryFilter();
  buildBrandFilter();
  initPrice();
  initRating();
  initClear();
  initToggle();
  apply();
})();
