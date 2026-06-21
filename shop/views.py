"""Public page views. Thin renderers — all data is loaded client-side via the
JSON API in ``api_views`` (kept). Page metadata lives here, not in JSON files."""

from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

NAV_LINKS = [
    {'href': '/', 'label': 'Home', 'key': 'home'},
    {'href': '/shop', 'label': 'Shop', 'key': 'shop'},
    {'href': '/services', 'label': 'Services', 'key': 'services'},
    {'href': '/about', 'label': 'About', 'key': 'about'},
    {'href': '/contact', 'label': 'Contact', 'key': 'contact'},
]


@ensure_csrf_cookie
def page(request, *, template, title, active=None, body_class='',
         splash=False, whatsapp=True, hero_preload=False):
    ctx = {
        'title': title,
        'active_nav': active,
        'nav_links': NAV_LINKS,
        'body_class': body_class,
        'show_splash': splash,
        'whatsapp_float': whatsapp,
        'hero_preload': hero_preload,
    }
    response = render(request, template, ctx)
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate'
    return response


def home(request):
    return page(request, template='pages/home.html',
                title='Jalaram Computers — Your One-Stop IT Solution',
                active='home', body_class='jc-landing',
                splash=True, hero_preload=True)


def shop(request):
    return page(request, template='pages/shop.html',
                title='Shop — Jalaram Computers', active='shop')


def product(request):
    return page(request, template='pages/product.html',
                title='Product — Jalaram Computers', active='shop')


def cart(request):
    return page(request, template='pages/cart.html',
                title='Your Cart — Jalaram Computers')


def checkout(request):
    return page(request, template='pages/checkout.html',
                title='Checkout — Jalaram Computers', whatsapp=False)


def order_confirmed(request):
    return page(request, template='pages/order-confirmed.html',
                title='Order Confirmed — Jalaram Computers', whatsapp=False)


def services(request):
    return page(request, template='pages/services.html',
                title='Services — Jalaram Computers', active='services')


def book_service(request):
    return page(request, template='pages/book-service.html',
                title='Book a Service — Jalaram Computers', active='services')


def about(request):
    return page(request, template='pages/about.html',
                title='About Us — Jalaram Computers', active='about')


def contact(request):
    return page(request, template='pages/contact.html',
                title='Contact — Jalaram Computers', active='contact')


def account(request):
    return page(request, template='pages/account.html',
                title='My Account — Jalaram Computers', whatsapp=False)
