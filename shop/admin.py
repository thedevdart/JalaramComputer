"""Jalaram Computers — Django admin (Phase 3).

Full store management via /admin: products, promos, orders, repairs,
bookings, customers, queries, settings, hero slides, newsletter.
Custom views: dashboard stats, order invoice, GST billing compiler.
"""
from datetime import timedelta
from decimal import Decimal

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import get_object_or_404, render
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from .models import (
    Brand,
    Category,
    ContactQuery,
    HeroSlideConfig,
    NewsletterSubscriber,
    Order,
    PageView,
    Product,
    ServiceBooking,
    ServiceRequest,
    SiteSettings,
)

User = get_user_model()

ORDER_STATUS_CHOICES = [
    'Processing', 'Paid', 'Shipped', 'Delivered', 'Cancelled', 'Refunded', 'Failed',
]
QUERY_STATUS_CHOICES = ['Open', 'In Progress', 'Resolved', 'Closed']
REPAIR_STATUS_CHOICES = ['Diagnosing', 'Awaiting Parts', 'Repairing', 'Ready', 'Delivered', 'Cancelled']


# ── Helpers ────────────────────────────────────────────────────────────────

_BR = mark_safe('<br>')


def _inr(val):
    return f'₹{Decimal(val or 0):,.0f}'


def _stacked(values):
    """Join values with <br>, escaping each (safe for user-supplied data)."""
    rows = [(v,) for v in values if v]
    return format_html_join(_BR, '{}', rows) or '—'


def _status_badge(status, tone='default'):
    colors = {
        'ok': '#16a34a', 'warn': '#d97706', 'err': '#dc2626',
        'info': '#2563eb', 'default': '#64748b',
    }
    bg = colors.get(tone, colors['default'])
    return format_html(
        '<span style="font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;'
        'padding:2px 8px;border-radius:999px;background:{}22;color:{};">{}</span>',
        bg, bg, status,
    )


def _order_status_tone(status):
    s = (status or '').lower()
    if s in ('paid', 'delivered'):
        return 'ok'
    if s in ('shipped', 'processing'):
        return 'info'
    if s in ('cancelled', 'failed', 'refunded'):
        return 'err'
    return 'warn'


# ── Custom AdminSite ───────────────────────────────────────────────────────

class JalaramAdminSite(admin.AdminSite):
    site_header = 'Jalaram Computers'
    site_title = 'Jalaram Admin'
    index_title = 'Store Dashboard'
    index_template = 'admin/jalaram_index.html'
    login_template = 'admin/jalaram_login.html'
    enable_nav_sidebar = False

    def get_urls(self):
        return [
            path('billing/', self.admin_view(billing_view), name='jalaram_billing'),
        ] + super().get_urls()

    def each_context(self, request):
        ctx = super().each_context(request)
        ctx['jalaram_stats'] = dashboard_stats()
        return ctx

    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['jalaram_analytics'] = analytics_stats()
        extra_context['recent_orders'] = list(Order.objects.all()[:6])
        extra_context['low_stock_products'] = list(
            Product.objects.filter(stock__lte=5).order_by('stock')[:6]
        )
        return super().index(request, extra_context=extra_context)


jalaram_admin = JalaramAdminSite(name='jalaram_admin')


def dashboard_stats():
    low_stock = Product.objects.filter(stock__lte=5).count()
    return {
        'products': Product.objects.count(),
        'orders': Order.objects.count(),
        'orders_unpaid': Order.objects.filter(paid=False).count(),
        'queries_open': ContactQuery.objects.filter(status__in=['Open', 'In Progress']).count(),
        'bookings': ServiceBooking.objects.count(),
        'repairs': ServiceRequest.objects.count(),
        'repairs_active': ServiceRequest.objects.exclude(status__in=['Delivered', 'Cancelled']).count(),
        'subscribers': NewsletterSubscriber.objects.count(),
        'low_stock': low_stock,
        'revenue': Order.objects.aggregate(t=Sum('total'))['t'] or 0,
    }


# ── Visitor analytics ───────────────────────────────────────────────────────

PAGE_NAMES = {
    '/': 'Home', '/shop': 'Shop', '/product': 'Product detail',
    '/cart': 'Cart', '/checkout': 'Checkout', '/order-confirmed': 'Order confirmed',
    '/services': 'Services', '/book-service': 'Book service',
    '/about': 'About', '/contact': 'Contact', '/account': 'Account',
}


def _page_name(path):
    return PAGE_NAMES.get(path, path)


def analytics_stats(days=14):
    """Aggregate PageView traffic for the dashboard: headline counts, a daily
    series for the bar chart, top pages, and a visit→order conversion rate."""
    today = timezone.localtime().date()
    start = today - timedelta(days=days - 1)
    d7 = today - timedelta(days=6)
    d30 = today - timedelta(days=29)

    all_views = PageView.objects.all()

    def _uniq(qs):
        return qs.values('visitor_id').distinct().count()

    today_qs = all_views.filter(created_at__date=today)
    views_7d_qs = all_views.filter(created_at__date__gte=d7)
    views_30d_qs = all_views.filter(created_at__date__gte=d30)

    # Daily counts for the chart (fill gaps with zero).
    rows = (all_views.filter(created_at__date__gte=start)
            .annotate(d=TruncDate('created_at'))
            .values('d').annotate(c=Count('id')))
    by_date = {r['d']: r['c'] for r in rows}
    counts = [by_date.get(start + timedelta(days=i), 0) for i in range(days)]
    peak = max(counts) or 1

    plot_h, top_pad, bar_w, gap = 96, 12, 26, 14
    step = bar_w + gap
    baseline = top_pad + plot_h
    bars = []
    for i, c in enumerate(counts):
        d = start + timedelta(days=i)
        h = round(plot_h * c / peak) if c else 0
        x = gap + i * step
        bars.append({
            'x': x, 'y': baseline - h, 'w': bar_w, 'h': h, 'count': c,
            'cx': x + bar_w / 2, 'label': d.strftime('%d'), 'is_today': d == today,
        })

    top_rows = views_30d_qs.values('path').annotate(c=Count('id')).order_by('-c')[:6]
    top_total = views_30d_qs.count() or 1
    top_pages = [{
        'path': r['path'], 'label': _page_name(r['path']),
        'count': r['c'], 'pct': round(100 * r['c'] / top_total),
    } for r in top_rows]

    visitors_30d = _uniq(views_30d_qs)
    orders_30d = Order.objects.filter(created_at__date__gte=d30).count()
    conversion = round(100 * orders_30d / visitors_30d, 1) if visitors_30d else 0

    return {
        'today_views': today_qs.count(),
        'today_visitors': _uniq(today_qs),
        'views_7d': views_7d_qs.count(),
        'visitors_7d': _uniq(views_7d_qs),
        'views_30d': views_30d_qs.count(),
        'visitors_30d': visitors_30d,
        'total_views': all_views.count(),
        'total_visitors': _uniq(all_views),
        'orders_30d': orders_30d,
        'conversion': conversion,
        'top_pages': top_pages,
        'days': days,
        'chart': {
            'width': days * step + gap, 'height': baseline + 22,
            'baseline': baseline, 'label_y': baseline + 16, 'peak': peak, 'bars': bars,
        },
    }


def billing_view(request):
    settings_obj = SiteSettings.load()
    if request.method == 'POST':
        items = []
        i = 0
        while True:
            desc = request.POST.get(f'item_{i}_desc')
            if desc is None:
                break
            if desc.strip():
                qty = int(request.POST.get(f'item_{i}_qty') or 1)
                price = Decimal(request.POST.get(f'item_{i}_price') or 0)
                tax = Decimal(request.POST.get(f'item_{i}_tax') or 18)
                items.append({
                    'desc': desc.strip(),
                    'qty': qty,
                    'price': price,
                    'tax': tax,
                    'line_total': price * qty,
                })
            i += 1
        subtotal = sum(it['line_total'] for it in items)
        gst = sum(it['line_total'] * it['tax'] / 100 for it in items)
        ctx = {
            **jalaram_admin.each_context(request),
            'shop': settings_obj,
            'customer': {
                'name': request.POST.get('cust_name', ''),
                'phone': request.POST.get('cust_phone', ''),
                'email': request.POST.get('cust_email', ''),
                'gstin': request.POST.get('cust_gstin', ''),
                'address': request.POST.get('cust_address', ''),
            },
            'items': items,
            'subtotal': subtotal,
            'gst': gst,
            'total': subtotal + gst,
            'print_mode': request.POST.get('action') == 'print',
        }
        return render(request, 'admin/billing_invoice.html', ctx)

    ctx = {
        **jalaram_admin.each_context(request),
        'shop': settings_obj,
        'title': 'GST Billing',
    }
    return render(request, 'admin/billing.html', ctx)


# ── Category & Brand ─────────────────────────────────────────────────────────

@admin.register(Category, site=jalaram_admin)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand, site=jalaram_admin)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'product_count')
    list_editable = ('is_active',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)

    fieldsets = (
        ('Brand', {'fields': ('name', 'slug', 'is_active')}),
        ('Logo (optional)', {'fields': ('logo_url',)}),
    )

    @admin.display(description='Products')
    def product_count(self, obj):
        return Product.objects.filter(brand=obj.name).count()


# ── Products ───────────────────────────────────────────────────────────────

class ProductAdminForm(forms.ModelForm):
    """Renders Brand and Category as dropdowns sourced from the Brand/Category
    tables. Both stay plain text on the model (the storefront filters on the
    name string), so the current value is always kept as a selectable option —
    even if that brand/category was later renamed or removed."""

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        brands = list(
            Brand.objects.filter(is_active=True).order_by('name').values_list('name', flat=True)
        )
        cats = list(Category.objects.order_by('name').values_list('name', flat=True))

        current_brand = (self.instance.brand or '').strip()
        current_cat = (self.instance.category or '').strip()
        if current_brand and current_brand not in brands:
            brands.insert(0, current_brand)
        if current_cat and current_cat not in cats:
            cats.insert(0, current_cat)

        self.fields['brand'].widget = forms.Select(
            choices=[('', '— Select brand —')] + [(b, b) for b in brands]
        )
        self.fields['category'].widget = forms.Select(
            choices=[('', '— Select category —')] + [(c, c) for c in cats]
        )
        self.fields['brand'].help_text = 'Add new brands under Brands; add categories under Categories.'
        self.fields['slug'].help_text = (
            'Auto-filled from the Name — this is the product’s web-address ID. '
            'Leave it as generated unless you have a reason to change it.'
        )


@admin.register(Product, site=jalaram_admin)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        'name', 'brand', 'category', 'price_display', 'stock', 'stock_level',
        'promo_display', 'badge', 'created_at',
    )
    list_filter = ('category', 'brand', 'badge')
    search_fields = ('name', 'brand', 'slug', 'details')
    list_editable = ('stock',)
    readonly_fields = ('created_at', 'image_preview', 'video_preview')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)
    actions = ['clear_promo_codes', 'mark_featured']

    fieldsets = (
        ('Product', {
            'fields': ('slug', 'name', 'brand', 'category', 'details', 'badge', 'stock'),
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'rating', 'rating_count'),
        }),
        ('Promo code', {
            'fields': ('promo_code', 'promo_discount'),
            'description': 'Optional product-level promo (percentage off).',
        }),
        ('Images & media', {
            'fields': (
                'image_icon', 'image_preview',
                'image1_file', 'image_url',
                'image2_file', 'image_url2',
                'image3_file', 'image_url3',
                'image4_file', 'image_url4',
                'images',
                'video', 'video_preview', 'video_url',
            ),
            'description': (
                'Upload images directly (stored on Cloudinary when configured). '
                'The URL field below each upload is a fallback — only used if no file is uploaded.'
            ),
        }),
        ('Meta', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    @admin.display(description='Price', ordering='price')
    def price_display(self, obj):
        if obj.original_price and obj.original_price > obj.price:
            return format_html('{} <span style="color:#94a3b8;text-decoration:line-through;">{}</span>',
                               _inr(obj.price), _inr(obj.original_price))
        return _inr(obj.price)

    @admin.display(description='Level')
    def stock_level(self, obj):
        if obj.stock == 0:
            return _status_badge('Out of stock', 'err')
        if obj.stock <= 5:
            return _status_badge('Low', 'warn')
        return _status_badge('OK', 'ok')

    @admin.display(description='Promo')
    def promo_display(self, obj):
        if obj.promo_code:
            return format_html('<strong>{}</strong> (−{}%)', obj.promo_code, obj.promo_discount)
        return '—'

    @admin.display(description='Preview')
    def image_preview(self, obj):
        src = obj.image1_src
        if src:
            return format_html('<img src="{}" style="max-height:80px;border-radius:4px;">', src)
        if obj.image_icon:
            return obj.image_icon
        return '—'

    @admin.display(description='Video preview')
    def video_preview(self, obj):
        src = obj.video_src
        if src:
            return format_html(
                '<video src="{}" controls preload="metadata" '
                'style="max-height:170px;border-radius:6px;background:#000;"></video>',
                src,
            )
        return '—'

    @admin.action(description='Clear promo codes on selected products')
    def clear_promo_codes(self, request, queryset):
        updated = queryset.update(promo_code='', promo_discount=0)
        self.message_user(request, f'Cleared promo on {updated} product(s).')

    @admin.action(description='Set badge to Featured')
    def mark_featured(self, request, queryset):
        updated = queryset.update(badge='Featured')
        self.message_user(request, f'Marked {updated} product(s) as Featured.')


class ProductPromo(Product):
    """Proxy — promo-code management view (products with active promos)."""

    class Meta:
        proxy = True
        verbose_name = 'promo code'
        verbose_name_plural = 'promo codes'


@admin.register(ProductPromo, site=jalaram_admin)
class ProductPromoAdmin(admin.ModelAdmin):
    list_display = ('name', 'promo_code', 'brand', 'promo_discount', 'price', 'net_price', 'stock')
    list_display_links = ('name',)
    list_filter = ('promo_code', 'brand')
    search_fields = ('promo_code', 'name', 'slug')
    list_editable = ('promo_code', 'promo_discount')
    ordering = ('promo_code',)

    fieldsets = (
        ('Promo', {'fields': ('promo_code', 'promo_discount')}),
        ('Product', {'fields': ('slug', 'name', 'brand', 'price', 'stock')}),
    )
    readonly_fields = ('slug', 'name', 'brand', 'price', 'stock')

    def get_queryset(self, request):
        return super().get_queryset(request).exclude(promo_code='')

    @admin.display(description='Net price')
    def net_price(self, obj):
        discount = Decimal(obj.promo_discount or 0) / 100
        return _inr(Decimal(obj.price) * (1 - discount))


# ── Orders ─────────────────────────────────────────────────────────────────

@admin.register(Order, site=jalaram_admin)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_id', 'customer_name', 'customer_email', 'status_badge', 'status',
        'total_display', 'paid_badge', 'item_count', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('order_id', 'customer', 'user_id_str')
    readonly_fields = (
        'order_id', 'created_at', 'items_preview', 'customer_preview',
        'shipping_preview', 'billing_preview', 'invoice_link',
    )
    ordering = ('-created_at',)
    actions = [
        'mark_processing', 'mark_paid', 'mark_shipped',
        'mark_delivered', 'mark_cancelled',
    ]
    fieldsets = (
        ('Order', {
            'fields': ('order_id', 'status', 'paid', 'date', 'user', 'user_id_str', 'invoice_link'),
        }),
        ('Totals', {
            'fields': ('subtotal', 'discount', 'gst', 'total'),
        }),
        ('Payment', {
            'fields': ('payment_method', 'payment_gateway', 'transaction_id'),
        }),
        ('Customer', {'fields': ('customer_preview', 'customer')}),
        ('Shipping', {'fields': ('shipping_preview', 'shipping_details')}),
        ('Billing', {'fields': ('billing_preview', 'billing_details')}),
        ('Line items', {'fields': ('items_preview', 'items')}),
        ('Meta', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def get_urls(self):
        urls = super().get_urls()
        return [
            path(
                '<path:object_id>/invoice/',
                self.admin_site.admin_view(self.invoice_view),
                name='shop_order_invoice',
            ),
        ] + urls

    def invoice_view(self, request, object_id):
        order = get_object_or_404(Order, pk=object_id)
        shop = SiteSettings.load()
        line_items = []
        for it in (order.items or []):
            qty = int(it.get('quantity') or 1)
            price = Decimal(str(it.get('price') or 0))
            line_items.append({**it, 'qty': qty, 'line_total': price * qty})
        return render(request, 'admin/order_invoice.html', {
            **self.admin_site.each_context(request),
            'order': order,
            'shop': shop,
            'line_items': line_items,
            'title': f'Invoice {order.order_id}',
        })

    @admin.display(description='Customer')
    def customer_name(self, obj):
        return (obj.customer or {}).get('name', '—')

    @admin.display(description='Email')
    def customer_email(self, obj):
        return (obj.customer or {}).get('email', '—')

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        return _status_badge(obj.status, _order_status_tone(obj.status))

    @admin.display(description='Total', ordering='total')
    def total_display(self, obj):
        return _inr(obj.total)

    @admin.display(description='Paid', boolean=True, ordering='paid')
    def paid_badge(self, obj):
        return obj.paid

    @admin.display(description='Items')
    def item_count(self, obj):
        return len(obj.items or [])

    @admin.display(description='View invoice')
    def invoice_link(self, obj):
        if not obj.pk:
            return '—'
        url = reverse('jalaram_admin:shop_order_invoice', args=[obj.pk])
        return format_html('<a href="{}" target="_blank" class="button">Open printable invoice</a>', url)

    @admin.display(description='Customer summary')
    def customer_preview(self, obj):
        c = obj.customer or {}
        name = c.get('name') or ''
        extra = _stacked([c.get('email'), c.get('phone')])
        if not name:
            return extra
        return format_html('<strong>{}</strong><br>{}', name, extra if extra != '—' else '')

    @admin.display(description='Shipping summary')
    def shipping_preview(self, obj):
        s = obj.shipping_details or {}
        return _stacked([s.get('address'), s.get('city'), s.get('state'), s.get('pincode'), s.get('method')])

    @admin.display(description='Billing summary')
    def billing_preview(self, obj):
        b = obj.billing_details or {}
        rows = [(k, v) for k, v in b.items() if v]
        return format_html_join(_BR, '{}: {}', rows) or '—'

    @admin.display(description='Items summary')
    def items_preview(self, obj):
        rows = [
            (it.get('name', 'Item'), it.get('quantity', 1), _inr((it.get('price', 0) or 0) * (it.get('quantity', 1) or 1)))
            for it in (obj.items or [])
        ]
        return format_html_join(_BR, '{} × {} — {}', rows) or '—'

    @admin.action(description='Mark as Processing')
    def mark_processing(self, request, queryset):
        queryset.update(status='Processing')

    @admin.action(description='Mark as Paid')
    def mark_paid(self, request, queryset):
        queryset.update(status='Paid', paid=True)

    @admin.action(description='Mark as Shipped')
    def mark_shipped(self, request, queryset):
        queryset.update(status='Shipped')

    @admin.action(description='Mark as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='Delivered', paid=True)

    @admin.action(description='Mark as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='Cancelled', paid=False)


# ── Repairs & bookings ─────────────────────────────────────────────────────

@admin.register(ServiceRequest, site=jalaram_admin)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = (
        'request_id', 'customer_name', 'service_type', 'device_model',
        'status', 'status_badge', 'cost', 'cost_display', 'date_created',
    )
    list_filter = ('status', 'service_type')
    search_fields = ('request_id', 'customer_name', 'phone', 'email')
    list_editable = ('status', 'cost')
    actions = ['mark_repairing', 'mark_ready', 'mark_delivered']

    fieldsets = (
        ('Ticket', {'fields': ('request_id', 'status', 'date_created')}),
        ('Customer', {'fields': ('customer_name', 'email', 'phone')}),
        ('Device & service', {'fields': ('service_type', 'device_model', 'description')}),
        ('Billing', {'fields': ('cost',)}),
    )

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        tone = 'ok' if obj.status in ('Ready', 'Delivered') else 'info'
        if obj.status == 'Cancelled':
            tone = 'err'
        return _status_badge(obj.status, tone)

    @admin.display(description='Cost', ordering='cost')
    def cost_display(self, obj):
        return _inr(obj.cost)

    @admin.action(description='Mark as Repairing')
    def mark_repairing(self, request, queryset):
        queryset.update(status='Repairing')

    @admin.action(description='Mark as Ready')
    def mark_ready(self, request, queryset):
        queryset.update(status='Ready')

    @admin.action(description='Mark as Delivered')
    def mark_delivered(self, request, queryset):
        queryset.update(status='Delivered')


@admin.register(ServiceBooking, site=jalaram_admin)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = (
        'booking_id', 'name', 'phone', 'service', 'date', 'slot', 'status',
        'promo_code', 'discount_applied', 'created_at',
    )
    list_editable = ('status',)
    list_filter = ('status', 'service', 'date')
    search_fields = ('booking_id', 'name', 'email', 'phone')
    readonly_fields = ('created_at',)
    actions = ['mark_confirmed', 'mark_completed', 'mark_cancelled']

    fieldsets = (
        ('Booking', {'fields': ('booking_id', 'service', 'date', 'slot', 'status')}),
        ('Customer', {'fields': ('name', 'phone', 'email')}),
        ('Details', {'fields': ('desc', 'promo_code', 'discount_applied')}),
        ('Meta', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    @admin.action(description='Mark as Confirmed')
    def mark_confirmed(self, request, queryset):
        queryset.update(status='Confirmed')

    @admin.action(description='Mark as Completed')
    def mark_completed(self, request, queryset):
        queryset.update(status='Completed')

    @admin.action(description='Mark as Cancelled')
    def mark_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')


# ── Customers (auth users) ─────────────────────────────────────────────────

@admin.register(User, site=jalaram_admin)
class CustomerAdmin(AuthUserAdmin):
    list_display = ('username', 'email', 'full_name', 'order_count', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    actions = ['grant_staff', 'revoke_staff']

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.get_full_name() or '—'

    @admin.display(description='Orders')
    def order_count(self, obj):
        return obj.orders.count()

    @admin.action(description='Grant staff access')
    def grant_staff(self, request, queryset):
        queryset.update(is_staff=True)

    @admin.action(description='Revoke staff access')
    def revoke_staff(self, request, queryset):
        queryset.update(is_staff=False)


# ── Contact queries ────────────────────────────────────────────────────────

@admin.register(ContactQuery, site=jalaram_admin)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'name', 'email', 'phone', 'category', 'status', 'status_badge', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('ticket_id', 'name', 'email', 'message')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    actions = ['mark_in_progress', 'mark_resolved', 'mark_closed']

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        tone = 'ok' if obj.status == 'Resolved' else 'info' if obj.status == 'Open' else 'default'
        return _status_badge(obj.status, tone)

    @admin.action(description='Mark In Progress')
    def mark_in_progress(self, request, queryset):
        queryset.update(status='In Progress')

    @admin.action(description='Mark Resolved')
    def mark_resolved(self, request, queryset):
        queryset.update(status='Resolved')

    @admin.action(description='Mark Closed')
    def mark_closed(self, request, queryset):
        queryset.update(status='Closed')


# ── Singletons: settings & hero ────────────────────────────────────────────

@admin.register(SiteSettings, site=jalaram_admin)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'gst', 'products_catalog_cleared')

    fieldsets = (
        ('Store identity', {'fields': ('name', 'email', 'phone')}),
        ('Address & GST', {'fields': ('addr1', 'addr2', 'gst')}),
        ('Catalog', {
            'fields': ('products_catalog_cleared',),
            'description': 'Set when the product catalog was intentionally cleared.',
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSlideConfig, site=jalaram_admin)
class HeroSlideConfigAdmin(admin.ModelAdmin):
    list_display = ('pk', 'auto_play_ms', 'slide_count')

    fieldsets = (
        ('Carousel', {'fields': ('auto_play_ms', 'slides')}),
    )

    @admin.display(description='Slides')
    def slide_count(self, obj):
        return len(obj.slides or [])

    def has_add_permission(self, request):
        return not HeroSlideConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ── Newsletter ─────────────────────────────────────────────────────────────

@admin.register(NewsletterSubscriber, site=jalaram_admin)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    readonly_fields = ('subscribed_at',)
    ordering = ('-subscribed_at',)


# ── Site visits (read-only analytics log) ────────────────────────────────────

@admin.register(PageView, site=jalaram_admin)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'page', 'visitor_short', 'visitor_type', 'referrer_short')
    list_filter = ('is_authenticated', 'created_at')
    search_fields = ('path', 'visitor_id', 'referrer')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='Page', ordering='path')
    def page(self, obj):
        return _page_name(obj.path)

    @admin.display(description='Visitor')
    def visitor_short(self, obj):
        return obj.visitor_id[:8]

    @admin.display(description='Type')
    def visitor_type(self, obj):
        return 'Logged in' if obj.is_authenticated else 'Guest'

    @admin.display(description='Came from')
    def referrer_short(self, obj):
        return (obj.referrer or '—')[:60]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Keep default admin site clean — all store models live on jalaram_admin.
for _model in (
    Brand, Category, Product, ProductPromo, Order, ServiceRequest, ServiceBooking,
    ContactQuery, SiteSettings, HeroSlideConfig, NewsletterSubscriber, PageView, User,
):
    if admin.site.is_registered(_model):
        admin.site.unregister(_model)
