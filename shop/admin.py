from django.contrib import admin

from .models import (
    ContactQuery,
    HeroSlideConfig,
    NewsletterSubscriber,
    Order,
    Product,
    ServiceBooking,
    ServiceRequest,
    SiteSettings,
)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'brand', 'category', 'price', 'stock')
    search_fields = ('name', 'brand', 'slug')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'status', 'total', 'paid', 'created_at')
    search_fields = ('order_id',)


@admin.register(ContactQuery)
class ContactQueryAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'name', 'email', 'status', 'created_at')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'customer_name', 'service_type', 'status')


@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'name', 'service', 'date')


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')


admin.site.register(SiteSettings)
admin.site.register(HeroSlideConfig)
