from django.urls import path

from . import api_views, page_views

urlpatterns = [
    # Public pages
    path('', page_views.render_page, {'route': '/'}, name='home'),
    path('shop', page_views.render_page, {'route': '/shop'}, name='shop'),
    path('product', page_views.render_page, {'route': '/product'}, name='product'),
    path('cart', page_views.render_page, {'route': '/cart'}, name='cart'),
    path('checkout', page_views.render_page, {'route': '/checkout'}, name='checkout'),
    path('order-confirmed', page_views.render_page, {'route': '/order-confirmed'}, name='order-confirmed'),
    path('services', page_views.render_page, {'route': '/services'}, name='services'),
    path('about', page_views.render_page, {'route': '/about'}, name='about'),
    path('contact', page_views.render_page, {'route': '/contact'}, name='contact'),
    path('account', page_views.render_page, {'route': '/account'}, name='account'),
    path('book-service', page_views.render_page, {'route': '/book-service'}, name='book-service'),
    path('admin', page_views.admin_page, name='admin-dashboard'),
    path('assets/images/hero/<str:filename>', page_views.hero_image, name='hero-image'),

    # Legacy HTML redirects
    path('index.html', page_views.render_page, {'route': '/'}),
    path('shop.html', page_views.render_page, {'route': '/shop'}),
    path('product.html', page_views.render_page, {'route': '/product'}),
    path('cart.html', page_views.render_page, {'route': '/cart'}),
    path('checkout.html', page_views.render_page, {'route': '/checkout'}),
    path('order-confirmed.html', page_views.render_page, {'route': '/order-confirmed'}),
    path('services.html', page_views.render_page, {'route': '/services'}),
    path('about.html', page_views.render_page, {'route': '/about'}),
    path('contact.html', page_views.render_page, {'route': '/contact'}),
    path('account.html', page_views.render_page, {'route': '/account'}),
    path('book-service.html', page_views.render_page, {'route': '/book-service'}),
    path('admin.html', page_views.admin_page),

    # Auth API
    path('api/auth/me/', api_views.auth_me, name='auth-me'),
    path('api/auth/register/', api_views.auth_register, name='auth-register'),
    path('api/auth/login/', api_views.auth_login, name='auth-login'),
    path('api/auth/logout/', api_views.auth_logout, name='auth-logout'),
    path('api/auth/admin-login/', api_views.admin_login, name='admin-login'),

    # Catalog & settings API
    path('api/products/', api_views.products_list, name='products-list'),
    path('api/products/<slug:product_id>/', api_views.products_detail, name='products-detail'),
    path('api/settings/shop/', api_views.settings_shop, name='settings-shop'),
    path('api/settings/shop/admin/', api_views.settings_shop_admin, name='settings-shop-admin'),
    path('api/settings/hero-slides/', api_views.settings_hero_slides, name='settings-hero'),
    path('api/settings/hero-slides/admin/', api_views.settings_hero_admin, name='settings-hero-admin'),

    # Orders, queries, services
    path('api/orders/', api_views.orders_collection, name='orders-list'),
    path('api/orders/<str:order_id>/', api_views.orders_detail, name='orders-detail'),
    path('api/queries/', api_views.queries_create, name='queries-create'),
    path('api/queries/list/', api_views.queries_list, name='queries-list'),
    path('api/services/', api_views.services_collection, name='services-list'),
    path('api/services/<str:request_id>/', api_views.services_detail, name='services-detail'),
    path('api/service-bookings/', api_views.service_bookings_create, name='service-bookings'),

    # Newsletter & admin sync
    path('api/newsletter/subscribe/', api_views.newsletter_subscribe, name='newsletter-subscribe'),
    path('api/admin/sync/', api_views.admin_bulk_sync, name='admin-sync'),
    path('api/admin/clear-products/', api_views.admin_clear_products, name='admin-clear-products'),
]
