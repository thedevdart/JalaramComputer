# Jalaram Computers Website — Client Brief

**Prepared for:** Jalaram Computers & IT Solutions  
**Purpose:** Where the website stands today, what that means for you, and sensible next steps before going live in India.

---

## What you have today

You have a **custom-built website** — not a template shop like Shopify. It includes:

- A **public storefront** — home page, product shop, product details, cart, checkout, services, contact
- An **admin panel** — add/edit products (with photos and video), view orders, promo codes, repair requests, billing, shop settings
- **Modern design** — works on mobile, professional look, ₹ pricing and GST details

This is a strong foundation. The **look and features** are largely ready. What needs attention is how the site **stores data, handles login, and takes payments** before real customers use it.

---

## How it works right now (in simple terms)

Today the website uses a **two-layer** setup:

| Layer | What it is | Think of it like… |
|-------|------------|-------------------|
| **Browser storage** | Data saved on each customer’s phone or computer | Notes on one device — not shared with others |
| **Firebase (Google cloud)** | Online database when configured | The shared ledger in the shop office |

**The issue:** The site currently treats the browser as the main copy, and tries to sync with the cloud. A proper live shop should work the other way around — **the cloud is the master copy**, and the browser only holds things like the shopping cart.

**Also important:** On your computer during development, the site runs with extra tooling that **automatically fixes** some things. The live hosting setup does not run that same tooling yet — so we must fix a few items **before** upload, or the live site may not behave like what you see on localhost.

---

## What works well ✅

- Professional pages and admin dashboard  
- Product catalog with images and video  
- Order management screens in admin  
- Firebase (cloud database) is already wired in  
- Deploy path to **Firebase Hosting** with your own domain (.in / .com)  
- Content fits an Indian shop — ₹, GST, Mumbai address, UPI-style checkout UI  

---

## What is not ready for real customers ⚠️

| Issue | Why it matters |
|-------|----------------|
| **Admin password is inside the website code** | Anyone technical could find it; not secure for a live business |
| **Payments are simulated** | Checkout looks real, but money is not verified through **Razorpay** (or similar) yet |
| **Demo behaviour** | New visitors may see sample items in the cart or sample products if the cloud is empty |
| **Data can get out of sync** | Admin on one device and the live shop might show different products if sync fails |
| **Customer accounts have a “fallback” mode** | If cloud login fails, the site can pretend the user is logged in — not a real account |
| **Live hosting not fully aligned with local testing** | Site must be adjusted so the shop works the same online as on your dev machine |

These are **fixable** — they do not mean starting over. They mean a focused improvement phase before launch.

---

## What you need before going live

**Minimum (must have):**

1. Website loads correctly on hosting — not only on the developer’s laptop  
2. Products and orders stored reliably in the **cloud**  
3. **Secure admin login** (Google / email — not a shared password in the code)  
4. **Real online payments** via **Razorpay** (UPI, cards, netbanking) with confirmation before an order is marked “Paid”  
5. Your **domain name** connected (e.g. jalaramcomputers.in) with HTTPS  

**Good to add soon after launch:**

- Order confirmation email to customer and shop  
- SMS or WhatsApp order alerts (optional)  
- Regular backup / export of orders  

---

## Hosting options (India context)

You will hear many hosting names in India. Here is what fits **this** website:

| Option | Fit for you | Rough cost |
|--------|-------------|------------|
| **Firebase Hosting + Firestore (Google)** | **Best fit** — already set up in this project; fast in India; works with your admin and database | Domain ~₹500–1,500/year + cloud usage often **₹0–2,000/month** early on |
| **Hostinger / BigRock / GoDaddy (cheap cPanel)** | **Poor fit** for this custom site — built for WordPress/PHP, not this codebase | ₹99–399/month — but extra work and split systems |
| **Shopify / WooCommerce** | **Different product** — ready-made shop; you would replace most of this custom site | ₹1,500–4,000+/month — fastest “standard” shop, less custom |
| **Own server (AWS Mumbai, etc.)** | **Later stage** — full control, more technical upkeep | ₹500–3,000+/month + developer time |

**Practical note:** For this project, **Firebase Hosting + Razorpay** is the most natural path — you keep the custom design and admin you already paid for, without rebuilding on WordPress or Shopify.

---

## Your options going forward

### Option A — Fix and launch on Firebase *(recommended)*

Keep the website you have. Fix security, payments, and cloud data. Deploy to Firebase with your domain.

| Pros | Cons |
|------|------|
| Keeps your custom design and admin | Needs developer time (roughly **2–4 weeks**) |
| Sensible for hosting **soon** | Small ongoing cloud cost |
| **Razorpay** fits Indian customers | Still custom code to maintain |
| Already aligned with how the site was built | |

**Best if:** You want *this* website live within weeks, with real payments and your admin panel.

---

### Option B — Host files on cheap Indian hosting + keep Firebase for data

Upload website files to Hostinger/BigRock; database stays on Firebase.

| Pros | Cons |
|------|------|
| Familiar Indian hosting; may include email | Two systems to manage |
| Low file-hosting price | Same code fixes still required |
| | More manual setup; no real advantage over Option A |

**Best if:** You already have cPanel hosting and insist on using it — otherwise Option A is simpler.

---

### Option C — Move to Shopify or WooCommerce

Use a ready-made e-commerce platform; this custom site becomes reference only.

| Pros | Cons |
|------|------|
| Fastest path to “standard” online selling | **Lose** most of the custom site and admin |
| Payments and admin built-in | Monthly platform fees |
| Less technical risk long-term | Design and features may not match 1:1 |

**Best if:** Launch date is **immediate** and custom admin is not essential.

---

### Option D — Bigger rebuild (proper server backend)

Build a full server system over 1–3 months — maximum control and security.

| Pros | Cons |
|------|------|
| “Enterprise-style” architecture | **Longest** timeline and cost |
| Easier to grow very large | Overkill before first launch |

**Best if:** You expect very high volume or strict compliance needs **after** an initial launch.

---

## Side-by-side at a glance

| | **A: Fix + Firebase** | **C: Shopify/Woo** |
|--|-------------------------|---------------------|
| **Time to live** | Weeks | Days to 1 week |
| **Keep custom admin** | Yes | No |
| **Keep current design** | Yes | Partially |
| **Real Razorpay payments** | After integration | Built-in |
| **Upfront dev work** | Moderate | Low (platform setup) |
| **Monthly running cost** | Low–medium | Medium |

---

## Our recommendation

**Option A — Fix and launch on Firebase** is the right balance for   Computers:

1. You already invested in a **custom site and admin** — Option A protects that investment.  
2. **Firebase + Mumbai region** performs well for Indian customers.  
3. **Razorpay** is the standard for UPI/cards and settles to your Indian bank account.  
4. Problems listed above are **targeted fixes**, not a full rebuild.

**Suggested sequence:**

1. **Week 1–2:** Fix live hosting parity, secure admin login, remove demo cart/products  
2. **Before taking payments:** Razorpay live account + verified checkout  
3. **Launch:** Connect domain, test on mobile data, go live with a small product set  
4. **After launch:** Emails, optional SMS, tidy up code for easier updates  

---

## Decisions we need from you

Please confirm:

1. **Target launch date** — e.g. this month / next month / flexible  
2. **Day-one payments** — full Razorpay online, or “order now, pay on delivery/WhatsApp” first?  
3. **Domain** — do you already own one (.in / .com)?  
4. **Razorpay** — is business KYC started or complete?  
5. **Priority** — keep this custom admin **yes/no**, or open to Shopify if faster?  

---

*For technical detail, see `docs/SITE-STATUS-AND-HOSTING-GUIDE.md` in the project folder.*
