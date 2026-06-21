/* Contact page — submit query to /api/queries/ */
import { saveContactQuery } from './api.js';

const form = document.getElementById('contact-form');
const formWrap = document.getElementById('contact-form-wrap');
const success = document.getElementById('contact-success');
const errorEl = document.getElementById('contact-error');
const submitBtn = document.getElementById('contact-submit');

function validate(data) {
  if (!data.name) return 'Please enter your name.';
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) return 'Please enter a valid email address.';
  if (!/^[0-9+\-\s]{7,15}$/.test(data.phone)) return 'Please enter a valid phone number.';
  if (!data.message) return 'Please enter your message.';
  return null;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  errorEl.textContent = '';
  const fd = new FormData(form);
  const data = Object.fromEntries([...fd.entries()].map(([k, v]) => [k, String(v).trim()]));
  const err = validate(data);
  if (err) { errorEl.textContent = err; return; }

  submitBtn.disabled = true;
  submitBtn.textContent = 'Submitting…';
  try {
    const res = await saveContactQuery({
      name: data.name,
      email: data.email,
      phone: data.phone,
      category: data.category,
      message: data.message,
      date: new Date().toLocaleDateString('en-IN', { year: 'numeric', month: 'long', day: 'numeric' }),
      status: 'Open',
    });
    const ticket = (res && res.query && res.query.ticketId) || 'JLR-QTK-PENDING';
    document.getElementById('cnt-success-ticket').textContent = ticket;
    formWrap.hidden = true;
    success.hidden = false;
  } catch (ex) {
    errorEl.textContent = (ex && ex.message) || 'Could not submit your query. Please try again.';
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Query';
  }
});
