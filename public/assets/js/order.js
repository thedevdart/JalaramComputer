/* Order confirmed — loads the saved order by id and renders the receipt. */
import { getOrder, formatINR } from './api.js';
import { esc } from './products.js';

const root = document.getElementById('order-root');
const id = new URLSearchParams(location.search).get('id') || sessionStorage.getItem('jc-last-order');

function addDays(n) {
  const d = new Date();
  d.setDate(d.getDate() + n);
  return d.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
}

function render(o) {
  const c = o.customer || {};
  const s = o.shippingDetails || {};
  const shipping = Math.max(0, (o.total || 0) - Math.max(0, (o.subtotal || 0) - (o.discount || 0)) - (o.gst || 0));
  const items = (o.items || []).map((it) => `<div class="jc-confirm__item">
    <div class="jc-confirm__item-media"><iconify-icon icon="${esc(it.imageIcon || 'lucide:box')}"></iconify-icon></div>
    <div class="jc-confirm__item-body"><p class="brand">${esc(it.brand || '')}</p><h4>${esc(it.name)}</h4><p class="qty">Quantity: ${it.quantity || 1}</p></div>
    <span class="jc-confirm__item-price">${formatINR((it.price || 0) * (it.quantity || 1))}</span>
  </div>`).join('');

  root.innerHTML = `
  <div class="jc-confirm__hero">
    <div class="jc-confirm__check"><iconify-icon icon="lucide:check"></iconify-icon></div>
    <span class="jc-confirm__eyebrow">Order Successful</span>
    <h1>Thank You for <em>Choosing Us</em></h1>
    <p>A confirmation has been sent to <span class="jc-confirm__email">${esc(c.email || 'your email')}</span>. Your order is being processed.</p>
  </div>

  <div class="jc-confirm__overview">
    <div><p class="k">Order Number</p><p class="v">#${esc(o.orderId)}</p></div>
    <div><p class="k">Order Date</p><p class="v">${esc(o.date || '')}</p></div>
    <div><p class="k">Payment Method</p><p class="v">${esc(o.paymentMethod || '')}</p></div>
  </div>

  <ol class="jc-confirm__timeline">
    <li class="is-active"><span><iconify-icon icon="lucide:file-text"></iconify-icon></span>Confirmed</li>
    <li class="is-active"><span><iconify-icon icon="lucide:package-search"></iconify-icon></span>Processing</li>
    <li><span><iconify-icon icon="lucide:truck"></iconify-icon></span>Shipped</li>
    <li><span><iconify-icon icon="lucide:home"></iconify-icon></span>Delivered</li>
  </ol>

  <div class="jc-confirm__grid">
    <div class="jc-confirm__main">
      <h3 class="jc-confirm__h">Order Summary</h3>
      <div class="jc-confirm__items">${items}</div>
      <div class="jc-confirm__breakdown">
        <h3 class="jc-confirm__h">Total Amount Breakdown</h3>
        <div class="jc-summary__row"><span>Subtotal</span><span>${formatINR(o.subtotal)}</span></div>
        ${o.discount ? `<div class="jc-summary__row"><span>Discount</span><span>−${formatINR(o.discount)}</span></div>` : ''}
        <div class="jc-summary__row"><span>Shipping &amp; Handling</span><span>${shipping ? formatINR(shipping) : 'FREE'}</span></div>
        <div class="jc-summary__row"><span>GST (18%)</span><span>${formatINR(o.gst)}</span></div>
        <div class="jc-confirm__total"><span>Total</span><span>${formatINR(o.total)}</span></div>
      </div>
    </div>

    <aside class="jc-confirm__aside">
      <div class="jc-confirm__delivery">
        <p class="k">Estimated Delivery</p>
        <h4>${addDays(5)}</h4>
        <p class="d">Estimated arrival between 10:00 AM – 6:00 PM</p>
        <a href="/contact" class="jc-btn jc-btn--accent jc-btn--block">Track My Order <iconify-icon icon="lucide:arrow-right"></iconify-icon></a>
      </div>
      <div class="jc-confirm__address">
        <h4>Shipping Address</h4>
        <p class="name">${esc(c.name || '')}</p>
        <p>${esc(s.address || '')}</p>
        <p>${esc([s.city, s.state].filter(Boolean).join(', '))}${s.pincode ? ' — ' + esc(s.pincode) : ''}</p>
        ${c.phone ? `<p class="phone"><span>Phone:</span> ${esc(c.phone)}</p>` : ''}
        <div class="jc-confirm__method"><iconify-icon icon="lucide:truck"></iconify-icon> ${esc(s.method || 'Standard Delivery')}</div>
      </div>
      <div class="jc-confirm__support">
        <h4>Need Assistance?</h4>
        <p>Our support team is ready to help with any queries about your order.</p>
        <a href="/contact" class="jc-btn jc-btn--ghost jc-btn--block">Contact Support</a>
      </div>
    </aside>
  </div>

  <div class="jc-confirm__actions">
    <a href="/shop" class="jc-btn jc-btn--navy"><iconify-icon icon="lucide:shopping-cart"></iconify-icon> Continue Shopping</a>
    <button type="button" id="print-invoice" class="jc-btn jc-btn--ghost"><iconify-icon icon="lucide:download"></iconify-icon> Download Invoice</button>
  </div>`;

  const print = document.getElementById('print-invoice');
  if (print) print.addEventListener('click', () => window.print());
  document.title = `Order ${o.orderId} Confirmed — Jalaram Computers`;
}

function fallback() {
  root.innerHTML = `<div class="jc-confirm__hero">
    <div class="jc-confirm__check"><iconify-icon icon="lucide:check"></iconify-icon></div>
    <span class="jc-confirm__eyebrow">Order Successful</span>
    <h1>Thank You for <em>Choosing Us</em></h1>
    <p>Your order has been placed. A confirmation will be sent to your email shortly.</p>
    <div class="jc-confirm__actions"><a href="/shop" class="jc-btn jc-btn--navy">Continue Shopping</a></div>
  </div>`;
}

(async function init() {
  if (!id) { fallback(); return; }
  try { render(await getOrder(id)); }
  catch { fallback(); }
})();
