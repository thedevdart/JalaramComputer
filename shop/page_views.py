import json
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET

NAV_LINKS = [
    {'key': 'home', 'href': '/', 'label': 'Home', 'id': 'nav-home-link'},
    {'key': 'shop', 'href': '/shop', 'label': 'Shop', 'id': 'nav-shop-link'},
    {'key': 'services', 'href': '/services', 'label': 'Services', 'id': 'nav-services-link'},
    {'key': 'about', 'href': '/about', 'label': 'About', 'id': 'nav-about-link'},
    {'key': 'contact', 'href': '/contact', 'label': 'Contact', 'id': 'nav-contact-link'},
]

ROUTE_NAV = {
    '/': 'home',
    '/shop': 'shop',
    '/product': 'shop',
    '/services': 'services',
    '/about': 'about',
    '/contact': 'contact',
    '/book-service': 'services',
    '/cart': None,
    '/checkout': None,
    '/order-confirmed': None,
    '/account': None,
}

PAGE_ROUTES = {
    '/': 'home',
    '/shop': 'shop',
    '/product': 'product',
    '/cart': 'cart',
    '/checkout': 'checkout',
    '/order-confirmed': 'order-confirmed',
    '/services': 'services',
    '/about': 'about',
    '/contact': 'contact',
    '/account': 'account',
    '/book-service': 'book-service',
}

META_DEFAULTS = {
    'title': 'Jalaram Computers',
    'body_class': 'bg-alabaster text-charcoal font-sans jc-site',
    'hero_preload': False,
    'page_css': [],
    'page_styles': None,
    'whatsapp_float': False,
    'scripts_partial': None,
}

PAGES_DIR = Path(settings.BASE_DIR) / 'templates' / 'pages'
META_DIR = Path(settings.BASE_DIR) / 'templates' / 'pages'


def nav_class(active_nav, key):
    base = 'text-sm tracking-widest uppercase font-medium transition-colors duration-500'
    inactive = f'text-silver hover:text-accent {base}'
    active = f'text-white border-b border-accent pb-1 {base}'
    return active if active_nav == key else inactive


def _load_meta(view_name):
    meta_path = META_DIR / f'{view_name}.meta.json'
    meta = dict(META_DEFAULTS)
    if meta_path.exists():
        with open(meta_path, encoding='utf-8') as f:
            raw = json.load(f)
        meta['title'] = raw.get('title', meta['title'])
        meta['body_class'] = raw.get('bodyClass', meta['body_class'])
        meta['hero_preload'] = raw.get('heroPreload', meta['hero_preload'])
        meta['page_css'] = raw.get('pageCss', meta['page_css'])
        meta['page_styles'] = raw.get('pageStyles')
        meta['whatsapp_float'] = raw.get('whatsappFloat', meta['whatsapp_float'])
        meta['scripts_partial'] = raw.get('scriptsPartial')
    return meta


def page_context(route):
    view_name = PAGE_ROUTES.get(route)
    if not view_name:
        return None
    meta = _load_meta(view_name)
    active_nav = ROUTE_NAV.get(route)
    return {
        'title': meta['title'],
        'body_class': meta['body_class'],
        'hero_preload': meta['hero_preload'],
        'page_css': meta['page_css'],
        'page_styles': meta['page_styles'],
        'whatsapp_float': meta['whatsapp_float'],
        'active_nav': active_nav,
        'nav_links': NAV_LINKS,
        'nav_class': nav_class,
        'scripts_partial': meta['scripts_partial'],
        'show_splash': route == '/',
    }


@ensure_csrf_cookie
def render_page(request, route):
    ctx = page_context(route)
    if not ctx:
        raise Http404('Page not found')
    view_name = PAGE_ROUTES[route]
    response = render(request, f'pages/{view_name}.html', ctx)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


@ensure_csrf_cookie
def admin_page(request):
    admin_path = Path(settings.BASE_DIR) / 'public' / 'admin.html'
    if not admin_path.exists():
        raise Http404('Admin page not found')
    html = admin_path.read_text(encoding='utf-8')
    html = html.replace('fonts-inter.css', 'fonts-fast.css')
    response = HttpResponse(html, content_type='text/html; charset=utf-8')
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


HERO_FALLBACKS = {
    'instant_support.jpg': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'instant_support_mobile.jpg': 'https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
    'networking_support.jpg': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'networking_support_mobile.jpg': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
    'printers_repair.jpg': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'printers_repair_mobile.jpg': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
    'computer_repair.jpg': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'computer_repair_mobile.jpg': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
    'laptop_repair.jpg': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'laptop_repair_mobile.jpg': 'https://images.unsplash.com/photo-1541807084-5c52b6b3adef?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
    'cctv_installation.jpg': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&w=1280&h=720&q=72&fm=jpg',
    'cctv_installation_mobile.jpg': 'https://images.unsplash.com/photo-1557597774-9d273605dfa9?auto=format&fit=crop&w=750&h=1200&q=72&fm=jpg',
}


def _hero_candidates(filename):
    base = filename.rsplit('.', 1)[0] if '.' in filename else filename
    ext = '.' + filename.rsplit('.', 1)[-1] if '.' in filename else ''
    names = {filename}
    if ext.lower() == '.webp':
        for variant in (f'{base}.webp', f'{base}.jpg', base.replace('-', '_') + '.webp',
                        base.replace('-', '_') + '.jpg', base.replace('_', '-') + '.webp',
                        base.replace('_', '-') + '.jpg'):
            names.add(variant)
    return list(names)


@require_GET
def hero_image(request, filename):
    hero_dir = Path(settings.BASE_DIR) / 'public' / 'assets' / 'images' / 'hero'
    for candidate in _hero_candidates(filename):
        local = hero_dir / candidate
        if local.exists():
            response = FileResponse(open(local, 'rb'))
            response['Cache-Control'] = 'public, max-age=604800, immutable'
            return response
    fallback = HERO_FALLBACKS.get(filename)
    if not fallback and filename.endswith('.webp'):
        fallback = HERO_FALLBACKS.get(filename.replace('.webp', '.jpg'))
    if fallback:
        from django.shortcuts import redirect
        return redirect(fallback, permanent=False)
    raise Http404()
