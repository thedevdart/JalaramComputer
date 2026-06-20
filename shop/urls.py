from django.urls import path

from . import api_views, views

urlpatterns = [
    # ── Public pages ──
    path('', views.home, name='home'),
    path('shop', views.shop, name='shop'),
    path('product', views.product, name='product'),
    path('cart', views.cart, name='cart'),
    path('checkout', views.checkout, name='checkout'),
    path('order-confirmed', views.order_confirmed, name='order-confirmed'),
    path('services', views.services, name='services'),
    path('book-service', views.book_service, name='book-service'),
    path('about', views.about, name='about'),
    path('contact', views.contact, name='contact'),
    path('account', views.account, name='account'),

    # ── Auth API ──
    path('api/auth/me/', api_views.auth_me, name='auth-me'),
    path('api/auth/register/', api_views.auth_register, name='auth-register'),
    path('api/auth/login/', api_views.auth_login, name='auth-login'),
    path('api/auth/logout/', api_views.auth_logout, name='auth-logout'),
    path('api/auth/admin-login/', api_views.admin_login, name='admin-login'),

    # ── Catalog & settings API ──
    path('api/products/', api_views.products_list, name='products-list'),
    path('api/products/<slug:product_id>/', api_views.products_detail, name='products-detail'),
    path('api/settings/shop/', api_views.settings_shop, name='settings-shop'),
    path('api/settings/shop/admin/', api_views.settings_shop_admin, name='settings-shop-admin'),
    path('api/settings/hero-slides/', api_views.settings_hero_slides, name='settings-hero'),
    path('api/settings/hero-slides/admin/', api_views.settings_hero_admin, name='settings-hero-admin'),

    # ── Orders, queries, services ──
    path('api/orders/', api_views.orders_collection, name='orders-list'),
    path('api/orders/<str:order_id>/', api_views.orders_detail, name='orders-detail'),
    path('api/queries/', api_views.queries_create, name='queries-create'),
    path('api/queries/list/', api_views.queries_list, name='queries-list'),
    path('api/services/', api_views.services_collection, name='services-list'),
    path('api/services/<str:request_id>/', api_views.services_detail, name='services-detail'),
    path('api/service-bookings/', api_views.service_bookings_create, name='service-bookings'),

    # ── Newsletter & admin sync ──
    path('api/newsletter/subscribe/', api_views.newsletter_subscribe, name='newsletter-subscribe'),
    path('api/admin/sync/', api_views.admin_bulk_sync, name='admin-sync'),
    path('api/admin/clear-products/', api_views.admin_clear_products, name='admin-clear-products'),
]
