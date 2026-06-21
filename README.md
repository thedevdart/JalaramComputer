# Jalaram Computers

A professional e-commerce + IT-services platform for Jalaram Computers, built on
**Django 5.2 + PostgreSQL**. No Node.js, no build step — clean Django templates,
one stylesheet, and small vanilla ES modules.

## Features

- **Storefront** — home (animated hero carousel + stacked sections), shop with
  live filters/sort/search, product detail, cart, checkout (GST + delivery),
  order confirmation, account (session auth + order history).
- **Services** — services overview, online service booking, contact form.
- **Admin** — full branded Django admin at `/admin`: products, promo codes,
  orders (status workflow + printable GST invoices), repairs, bookings,
  customers, queries, store settings, hero slides, newsletter, and a GST
  billing tool.
- **Production-ready** — WhiteNoise static serving, security headers, error
  pages, server-authoritative order IDs.

## Quick start (local)

```powershell
pip install -r requirements.txt
copy .env.example .env          # then edit DB credentials if needed
python manage.py migrate
python manage.py ensure_admin   # creates jcowner / admin123 (local default)
python manage.py runserver
```

Open http://localhost:8000 · Admin → http://localhost:8000/admin

> No products are pre-seeded. Add your catalogue through the admin — products
> appear on the storefront immediately.

**No PostgreSQL handy?** Run against SQLite for a quick spin:

```powershell
$env:USE_SQLITE="true"; python manage.py migrate; python manage.py ensure_admin; python manage.py runserver
```

## Configuration (`.env`)

| Variable | Purpose |
| --- | --- |
| `DEBUG` | `true` for dev, `false` in production |
| `DJANGO_SECRET_KEY` | **set a long random value in production** |
| `ALLOWED_HOSTS` | comma-separated hostnames |
| `POSTGRES_*` / `DATABASE_URL` | database connection |
| `ADMIN_EMAIL` | email treated as staff for the storefront API |
| `SMTP_*`, `MAIL_FROM` | newsletter email (optional) |
| `CSRF_TRUSTED_ORIGINS` | comma-separated https origins (production) |

## Railway deploy (one-click)

This repo includes `railway.toml`, `Procfile`, `runtime.txt`, and auto-detection of
`DATABASE_URL` / `RAILWAY_PUBLIC_DOMAIN`. Nixpacks auto-detects Python from
`requirements.txt` — do not add a custom `nixpacks.toml` unless you know what
you are doing (it can break `pip`).

### Steps

1. **New project** on [Railway](https://railway.app) → **Deploy from GitHub** → select this repo → branch `main`.
2. **Add PostgreSQL** — Railway dashboard → **+ New** → **Database** → **PostgreSQL**.
3. **Link database** — open your **web service** → **Variables** → **+ New Variable** → **Add Reference** → select Postgres service → `DATABASE_URL`.
4. **Set variables** (required — deploy will fail without these):

   | Variable | Value |
   | --- | --- |
   | `DEBUG` | `false` |
   | `DJANGO_SECRET_KEY` | long random string (50+ chars) |

   Railway auto-sets `RAILWAY_PUBLIC_DOMAIN`, `PORT`, and `DATABASE_URL` when Postgres is linked.

5. **Deploy** — on each deploy the start script runs `migrate`, `collectstatic`, then Gunicorn.

6. **Create admin** — either set Railway variables and redeploy:

   | Variable | Value |
   | --- | --- |
   | `ADMIN_USERNAME` | `jcowner` |
   | `ADMIN_EMAIL` | contact email (optional, not used to sign in) |
   | `ADMIN_PASSWORD` | your admin password |

   The start script runs `ensure_admin` automatically when `ADMIN_PASSWORD` is set. Only one superuser is kept (`jcowner` by default); any others are demoted.

   **Or** run once in the Railway shell (must use the Nixpacks venv — plain `python` has no Django):

   ```bash
   export PATH="/opt/venv/bin:$PATH"
   python manage.py ensure_admin --username jcowner --password 'your-password'
   ```

   One-liner without exporting PATH:

   ```bash
   /opt/venv/bin/python manage.py ensure_admin --username jcowner --password 'your-password'
   ```

Open the generated `*.up.railway.app` URL. Admin → `/admin`.

## Google Sign-In (customer accounts)

Customers can sign up or sign in with Google on `/account`. Admin login at `/admin/` stays username/password only.

1. Open [Google Cloud Console](https://console.cloud.google.com/) → create or select a project.
2. **APIs & Services → OAuth consent screen** — choose **External**, fill app name (e.g. Jalaram Computers), support email, and add your domain under authorized domains if prompted. Add scopes: `email`, `profile`, `openid` (defaults for Sign in with Google).
3. **APIs & Services → Credentials → Create credentials → OAuth client ID** — type **Web application**.
4. **Authorized JavaScript origins** (add every URL users visit):
   - `http://localhost:8000` (local dev)
   - `https://www.jalaramcomputers.com`
   - `https://jalaramcomputers.com`
   - Your Railway URL, e.g. `https://your-app.up.railway.app`
5. Copy the **Client ID** (ends in `.apps.googleusercontent.com`). You do **not** need the client secret for this flow.
6. Set environment variable:
   - Local: add `GOOGLE_OAUTH_CLIENT_ID=...` to `.env`
   - Railway: add `GOOGLE_OAUTH_CLIENT_ID` under Variables and redeploy

If the variable is missing, email/password auth still works; the Google button is hidden.

**Publishing:** While the OAuth app is in **Testing**, only Google accounts you add as test users can sign in. When ready for everyone, submit the consent screen for verification (or move to Production if your use case allows without full verification).

## Production deploy (generic)

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py ensure_admin --username jcowner --password '<strong>'
gunicorn config.wsgi:application
```

Set `DEBUG=false`, a real `DJANGO_SECRET_KEY`, and `ALLOWED_HOSTS`. With
`DEBUG=false` the app enables HTTPS redirect, secure cookies and HSTS, and
WhiteNoise serves the compressed static files. Verify with
`python manage.py check --deploy`.

## Project layout

```
config/        Django project (settings, urls, wsgi/asgi)
shop/          app — models, page views, JSON API (api_views), admin
templates/     base + partials + pages + admin
public/assets/ app.css, ES modules (api/cart/shop/product/checkout/…), images
```

## Stack

- Django 5.2 · PostgreSQL · WhiteNoise · Gunicorn
- Vanilla ES-module JavaScript (no framework, no bundler)
- One design-system stylesheet (`public/assets/css/app.css`)
