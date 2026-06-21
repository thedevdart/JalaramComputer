"""Phase 3 smoke test — Django admin CRUD + custom views."""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import Client

from shop.models import ContactQuery, Order, Product, ServiceBooking, SiteSettings

User = get_user_model()

# Ensure testserver is allowed
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS = [*settings.ALLOWED_HOSTS, 'testserver']


def main():
    email = 'phase3admin@example.com'
    User.objects.filter(email=email).delete()
    admin_user = User.objects.create_superuser(
        username='phase3admin', email=email, password='admin123',
    )

    client = Client()
    assert client.login(username='phase3admin', password='admin123'), 'admin login failed'

    pages = [
        '/admin/',
        '/admin/shop/product/',
        '/admin/shop/productpromo/',
        '/admin/shop/order/',
        '/admin/shop/servicerequest/',
        '/admin/shop/servicebooking/',
        '/admin/shop/contactquery/',
        '/admin/shop/newslettersubscriber/',
        '/admin/shop/sitesettings/',
        '/admin/shop/heroslideconfig/',
        '/admin/auth/user/',
        '/admin/billing/',
    ]
    for path in pages:
        r = client.get(path)
        assert r.status_code == 200, f'{path} -> {r.status_code}'
    print('Admin pages: all 200')

    SiteSettings.load()
    slug = 'phase3-test-product'
    Product.objects.filter(slug=slug).delete()
    r = client.post('/admin/shop/product/add/', {
        'slug': slug,
        'name': 'Phase 3 Test Laptop',
        'brand': 'HP',
        'category': 'Laptops',
        'price': '45999',
        'original_price': '52999',
        'rating': '4.5',
        'rating_count': '12',
        'badge': 'Featured',
        'details': '16GB RAM, 512GB SSD',
        'stock': '10',
        'promo_code': 'LAPTOP10',
        'promo_discount': '10',
        'image_icon': 'lucide:laptop',
        'image_url': '',
        'image_url2': '',
        'image_url3': '',
        'image_url4': '',
        'images': '[]',
        'video_url': '',
    }, follow=True)
    assert r.status_code == 200
    assert Product.objects.filter(slug=slug).exists()
    print('Product CRUD: create OK')

    r = client.get('/api/products/')
    assert r.status_code == 200
    ids = [p['id'] for p in r.json()]
    assert slug in ids
    print('Storefront API: product visible')

    order = Order.objects.filter(order_id='JC-2026-9999').first()
    if order:
        r = client.get(f'/admin/shop/order/{order.pk}/invoice/')
        assert r.status_code == 200
        assert order.order_id in r.content.decode()
        print('Order invoice view: OK')

    Product.objects.filter(slug=slug).delete()
    admin_user.delete()
    print('Phase 3 smoke test: ALL PASSED')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as e:
        print(f'FAILED: {e}', file=sys.stderr)
        sys.exit(1)
