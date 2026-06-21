"""Create or update a staff admin user for /admin access."""
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from shop.models import SiteSettings


class Command(BaseCommand):
    help = 'Create a staff superuser for Jalaram admin (defaults: admin@jalaram.local / admin123).'

    def add_arguments(self, parser):
        parser.add_argument('--email', default='admin@jalaram.local')
        parser.add_argument('--password', default='admin123')
        parser.add_argument('--username', default='admin')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email'].strip().lower()
        username = options['username']
        password = options['password']

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.filter(username=username).first()

        if user:
            user.is_staff = True
            user.is_superuser = True
            user.email = email
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Updated staff user: {user.username} ({email})'))
        else:
            user = User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Created superuser: {username} ({email})'))

        SiteSettings.load()
        self.stdout.write('Admin URL: http://127.0.0.1:8000/admin/')
