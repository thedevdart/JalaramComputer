/* Book a Service — appointment form → /api/service-bookings/ */
import { saveServiceBooking, authMe } from './api.js';

const form = document.getElementById('booking-form');
const success = document.getElementById('booking-success');
const errorEl = document.getElementById('booking-error');
const submitBtn = document.getElementById('booking-submit');
const promoInput = document.getElementById('booking-promo');
const promoApplied = document.getElementById('booking-promo-applied');
const dateInput = document.getElementById('booking-date');

let promoActive = false;
let validatedDiscount = 0;

function setMinDate() {
  const d = new Date();
  dateInput.min = d.toISOString().slice(0, 10);
}

function validate(data) {
  if (!data.name) return 'Please enter your full name.';
  if (!/^[0-9+\-\s]{7,15}$/.test(data.phone)) return 'Please enter a valid phone number.';
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) return 'Please enter a valid email address.';
  if (!data.service) return 'Please select a service type.';
  if (!data.date) return 'Please choose a preferred date.';
  if (!data.slot) return 'Please choose a time slot.';
  if (!data.desc) return 'Please describe your issue.';
  return null;
}

document.getElementById('apply-booking-promo').addEventListener('click', async () => {
  const code = promoInput.value.trim().toUpperCase();
  if (!code) { errorEl.textContent = 'Enter a promo code to apply.'; return; }
  errorEl.textContent = '';
  try {
    const res = await fetch('/api/service-bookings/validate-promo/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || '' },
      body: JSON.stringify({ code }),
    });
    const json = await res.json();
    if (json.ok) {
      promoActive = true;
      validatedDiscount = json.discount;
      promoApplied.hidden = false;
      promoInput.value = code;
    } else {
      promoActive = false;
      validatedDiscount = 0;
      promoApplied.hidden = true;
      errorEl.textContent = json.error || 'Invalid promo code.';
    }
  } catch {
    errorEl.textContent = 'Could not validate promo code. Please try again.';
  }
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorEl.textContent = '';
  const data = {
    name: document.getElementById('booking-name').value.trim(),
    phone: document.getElementById('booking-phone').value.trim(),
    email: document.getElementById('booking-email').value.trim(),
    service: document.getElementById('booking-service').value,
    date: document.getElementById('booking-date').value,
    slot: document.getElementById('booking-time').value,
    desc: document.getElementById('booking-desc').value.trim(),
  };
  const err = validate(data);
  if (err) { errorEl.textContent = err; return; }

  submitBtn.disabled = true;
  submitBtn.innerHTML = '<iconify-icon icon="lucide:loader-2" class="jc-spin"></iconify-icon> Processing…';
  try {
    const payload = {
      name: data.name,
      phone: data.phone,
      email: data.email,
      service: data.service,
      date: data.date,
      slot: data.slot,
      desc: data.desc,
      promoCode: promoActive ? promoInput.value.trim().toUpperCase() : '',
      discountApplied: promoActive ? validatedDiscount : 0,
    };
    const res = await saveServiceBooking(payload);
    const booking = (res && res.booking) || {};
    document.getElementById('success-booking-id').textContent = booking.bookingId || '—';
    document.getElementById('success-booking-service').textContent = booking.service || data.service;
    document.getElementById('success-booking-date').textContent = booking.date || data.date;
    document.getElementById('success-booking-time').textContent = booking.slot || data.slot;
    const discountEl = document.getElementById('success-booking-discount');
    if (discountEl) { discountEl.hidden = !(booking.discountApplied > 0); }
    form.hidden = true;
    success.hidden = false;
  } catch (ex) {
    errorEl.textContent = (ex && ex.message) || 'Could not confirm your appointment. Please try again.';
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<iconify-icon icon="lucide:calendar-check"></iconify-icon> Confirm Appointment';
  }
});

async function prefillFromAccount() {
  try {
    const user = await authMe();
    if (!user) return;
    const emailEl = document.getElementById('booking-email');
    if (!emailEl.value) emailEl.value = user.email || '';
    const nameEl = document.getElementById('booking-name');
    if (!nameEl.value && user.displayName) nameEl.value = user.displayName;
  } catch { /* anonymous */ }
}

setMinDate();
prefillFromAccount();

// Pre-select service from URL ?service=
const svc = new URLSearchParams(location.search).get('service');
if (svc) {
  const sel = document.getElementById('booking-service');
  for (const opt of sel.options) {
    if (opt.value.toLowerCase().includes(svc.toLowerCase())) {
      sel.value = opt.value;
      break;
    }
  }
}
