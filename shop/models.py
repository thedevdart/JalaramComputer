from django.conf import settings
from django.db import models


class Category(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    slug = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    original_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rating = models.FloatField(default=0)
    rating_count = models.PositiveIntegerField(default=0)
    badge = models.CharField(max_length=50, blank=True, default='')
    details = models.TextField(blank=True, default='')
    stock = models.PositiveIntegerField(default=0)
    promo_code = models.CharField(max_length=50, blank=True, default='')
    promo_discount = models.PositiveIntegerField(default=0)
    image_url = models.URLField(max_length=500, blank=True, default='')
    image_url2 = models.URLField(max_length=500, blank=True, default='')
    image_url3 = models.URLField(max_length=500, blank=True, default='')
    image_url4 = models.URLField(max_length=500, blank=True, default='')
    images = models.JSONField(default=list, blank=True)
    video_url = models.URLField(max_length=500, blank=True, default='')
    image_icon = models.CharField(max_length=100, blank=True, default='lucide:box')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def to_frontend(self):
        return {
            'id': self.slug,
            'name': self.name,
            'brand': self.brand,
            'category': self.category,
            'price': float(self.price),
            'originalPrice': float(self.original_price) if self.original_price else float(self.price),
            'rating': self.rating,
            'ratingCount': self.rating_count,
            'badge': self.badge,
            'details': self.details,
            'stock': self.stock,
            'promoCode': self.promo_code,
            'promoDiscount': self.promo_discount,
            'imageUrl': self.image_url,
            'imageUrl2': self.image_url2,
            'imageUrl3': self.image_url3,
            'imageUrl4': self.image_url4,
            'images': self.images or [],
            'videoUrl': self.video_url,
            'imageIcon': self.image_icon,
            'createdAt': int(self.created_at.timestamp() * 1000),
        }


class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders',
    )
    user_id_str = models.CharField(max_length=100, blank=True, default='')
    date = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='Paid')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    customer = models.JSONField(default=dict)
    shipping_details = models.JSONField(default=dict, blank=True)
    billing_details = models.JSONField(default=dict, blank=True)
    items = models.JSONField(default=list)
    payment_method = models.CharField(max_length=200, blank=True, default='')
    transaction_id = models.CharField(max_length=200, blank=True, default='')
    payment_gateway = models.CharField(max_length=100, blank=True, default='')
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.order_id

    def to_frontend(self):
        return {
            'orderId': self.order_id,
            'userId': self.user_id_str or (str(self.user_id) if self.user_id else ''),
            'date': self.date,
            'status': self.status,
            'subtotal': float(self.subtotal),
            'discount': float(self.discount),
            'gst': float(self.gst),
            'total': float(self.total),
            'customer': self.customer,
            'shippingDetails': self.shipping_details,
            'billingDetails': self.billing_details,
            'items': self.items,
            'paymentMethod': self.payment_method,
            'transactionId': self.transaction_id,
            'paymentGateway': self.payment_gateway,
            'paid': self.paid,
        }


class ContactQuery(models.Model):
    ticket_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    category = models.CharField(max_length=100)
    message = models.TextField()
    date = models.CharField(max_length=100)
    status = models.CharField(max_length=50, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'contact queries'
        ordering = ['-created_at']

    def to_frontend(self):
        return {
            'ticketId': self.ticket_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'category': self.category,
            'message': self.message,
            'date': self.date,
            'status': self.status,
        }


class ServiceRequest(models.Model):
    request_id = models.CharField(max_length=50, unique=True)
    customer_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30)
    service_type = models.CharField(max_length=100)
    device_model = models.CharField(max_length=200, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=50, default='Diagnosing')
    cost = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date_created = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def to_frontend(self):
        return {
            'requestId': self.request_id,
            'customerName': self.customer_name,
            'email': self.email,
            'phone': self.phone,
            'serviceType': self.service_type,
            'deviceModel': self.device_model,
            'description': self.description,
            'status': self.status,
            'cost': float(self.cost),
            'dateCreated': self.date_created,
        }


class ServiceBooking(models.Model):
    booking_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default='')
    service = models.CharField(max_length=100)
    date = models.CharField(max_length=100)
    slot = models.CharField(max_length=100)
    desc = models.TextField(blank=True, default='')
    promo_code = models.CharField(max_length=50, blank=True, default='')
    discount_applied = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def to_frontend(self):
        return {
            'bookingId': self.booking_id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'service': self.service,
            'date': self.date,
            'slot': self.slot,
            'desc': self.desc,
            'promoCode': self.promo_code or None,
            'discountApplied': float(self.discount_applied),
        }


class SiteSettings(models.Model):
    """Singleton store configuration."""

    name = models.CharField(max_length=200, default='Jalaram Computers & IT Solutions')
    addr1 = models.CharField(max_length=300, default='Shop No. 5-7, Jalaram Arcade, Lamington Road')
    addr2 = models.CharField(max_length=300, default='Mumbai, Maharashtra - 400007')
    gst = models.CharField(max_length=50, default='27AACJC2026P1Z3')
    email = models.EmailField(default='jalaramcomputers21@gmail.com')
    phone = models.CharField(max_length=30, default='+91 98928 48643')
    products_catalog_cleared = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'site settings'
        verbose_name_plural = 'site settings'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def to_frontend(self):
        return {
            'name': self.name,
            'addr1': self.addr1,
            'addr2': self.addr2,
            'gst': self.gst,
            'email': self.email,
            'phone': self.phone,
            'products_catalog_cleared': self.products_catalog_cleared,
        }


class HeroSlideConfig(models.Model):
    """Singleton hero carousel configuration."""

    auto_play_ms = models.PositiveIntegerField(default=4500)
    slides = models.JSONField(default=list)

    class Meta:
        verbose_name = 'hero slide config'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def to_frontend(self):
        return {
            'autoPlayMs': self.auto_play_ms,
            'slides': self.slides,
        }


class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
