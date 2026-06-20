import json
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import HeroSlideConfig, Product, SiteSettings
from shop.serializers import product_from_frontend

User = get_user_model()


DEFAULT_PRODUCTS = [
    {
        'id': 'hp-pavilion-15',
        'name': 'HP Pavilion 15 Core i5',
        'brand': 'HP',
        'category': 'Laptops',
        'price': 53000,
        'originalPrice': 60000,
        'rating': 4.5,
        'ratingCount': 48,
        'badge': 'Bestseller',
        'details': '8GB | 512GB SSD | Silver',
        'stock': 15,
        'promoCode': 'LAPTOP10',
        'promoDiscount': 10,
        'imageUrl': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?auto=format&fit=crop&w=600&q=80',
        'imageIcon': 'lucide:laptop',
    },
    {
        'id': 'dell-inspiron-14',
        'name': 'Dell Inspiron 14 Plus',
        'brand': 'Dell',
        'category': 'Laptops',
        'price': 62000,
        'originalPrice': 68000,
        'rating': 4.4,
        'ratingCount': 32,
        'badge': 'New',
        'details': '16GB | 512GB SSD | Graphite',
        'stock': 10,
        'imageUrl': 'https://images.unsplash.com/photo-1593642632823-8f785ba67e45?auto=format&fit=crop&w=600&q=80',
        'imageIcon': 'lucide:laptop',
    },
    {
        'id': 'logitech-mx-master',
        'name': 'Logitech MX Master 3S',
        'brand': 'Logitech',
        'category': 'Accessories',
        'price': 8995,
        'originalPrice': 9995,
        'rating': 4.8,
        'ratingCount': 120,
        'badge': 'Hot',
        'details': 'Wireless | Bluetooth | Graphite',
        'stock': 25,
        'imageUrl': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?auto=format&fit=crop&w=600&q=80',
        'imageIcon': 'lucide:mouse',
    },
    {
        'id': 'canon-pixma-g3000',
        'name': 'Canon PIXMA G3000',
        'brand': 'Canon',
        'category': 'Printers',
        'price': 14500,
        'originalPrice': 16500,
        'rating': 4.3,
        'ratingCount': 56,
        'badge': 'Featured',
        'details': 'Ink Tank | Wi-Fi | Print/Scan/Copy',
        'stock': 8,
        'imageUrl': 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?auto=format&fit=crop&w=600&q=80',
        'imageIcon': 'lucide:printer',
    },
]


class Command(BaseCommand):
    help = 'Seed database with default products, hero slides, and admin user'

    def add_arguments(self, parser):
        parser.add_argument('--admin-password', default='Jalaram@Admin2026!')

    def handle(self, *args, **options):
        SiteSettings.load()
        self.stdout.write('Site settings ready.')

        hero_path = Path('public/data/hero-services.json')
        if hero_path.exists():
            data = json.loads(hero_path.read_text(encoding='utf-8'))
            config = HeroSlideConfig.load()
            config.auto_play_ms = data.get('autoPlayMs', 4500)
            config.slides = data.get('slides', [])
            config.save()
            self.stdout.write(f'Seeded {len(config.slides)} hero slides.')

        if not Product.objects.exists():
            for item in DEFAULT_PRODUCTS:
                fields = product_from_frontend(item)
                Product.objects.create(**fields)
            self.stdout.write(f'Seeded {len(DEFAULT_PRODUCTS)} products.')
        else:
            self.stdout.write('Products already exist — skipped.')

        admin_email = 'support@jalaramcomputers.com'
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': admin_email, 'is_staff': True, 'is_superuser': True},
        )
        if created or not user.check_password(options['admin_password']):
            user.set_password(options['admin_password'])
            user.email = admin_email
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(
                f'Admin user ready (username: admin, email: {admin_email})'
            ))
        else:
            self.stdout.write('Admin user already exists.')
