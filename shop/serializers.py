"""Helpers to parse frontend payloads into model fields."""

from decimal import Decimal, InvalidOperation


def _dec(value, default=0):
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal(default)


def product_from_frontend(data):
    slug = data.get('id') or data.get('slug')
    if not slug:
        raise ValueError('Product id is required')
    return {
        'slug': slug,
        'name': data.get('name', ''),
        'brand': data.get('brand', ''),
        'category': data.get('category', ''),
        'price': _dec(data.get('price')),
        'original_price': _dec(data.get('originalPrice', data.get('price'))),
        'rating': float(data.get('rating') or 0),
        'rating_count': int(data.get('ratingCount') or 0),
        'badge': data.get('badge') or '',
        'details': data.get('details') or '',
        'stock': int(data.get('stock') or 0),
        'promo_code': data.get('promoCode') or '',
        'promo_discount': int(data.get('promoDiscount') or 0),
        'image_url': data.get('imageUrl') or '',
        'image_url2': data.get('imageUrl2') or '',
        'image_url3': data.get('imageUrl3') or '',
        'image_url4': data.get('imageUrl4') or '',
        'images': data.get('images') or [],
        'video_url': data.get('videoUrl') or '',
        'image_icon': data.get('imageIcon') or 'lucide:box',
    }


def order_from_frontend(data, user=None):
    customer = data.get('customer') or {}
    return {
        'order_id': data['orderId'],
        'user': user,
        'user_id_str': data.get('userId') or '',
        'date': data.get('date', ''),
        'status': data.get('status', 'Processing'),  # _recalculate_order always sets this
        'subtotal': _dec(data.get('subtotal')),
        'discount': _dec(data.get('discount')),
        'gst': _dec(data.get('gst')),
        'total': _dec(data.get('total')),
        'customer': customer,
        'shipping_details': data.get('shippingDetails') or {},
        'billing_details': data.get('billingDetails') or {},
        'items': data.get('items') or [],
        'payment_method': data.get('paymentMethod') or '',
        'transaction_id': data.get('transactionId') or '',
        'payment_gateway': data.get('paymentGateway') or '',
        'paid': bool(data.get('paid')),
    }


def service_request_from_frontend(data):
    return {
        'request_id': data['requestId'],
        'customer_name': data.get('customerName') or data.get('customer_name') or '',
        'email': data.get('email') or '',
        'phone': data.get('phone') or '',
        'service_type': data.get('serviceType') or data.get('service_type') or '',
        'device_model': data.get('deviceModel') or data.get('device_model') or '',
        'description': data.get('description') or '',
        'status': data.get('status') or 'Diagnosing',
        'cost': _dec(data.get('cost')),
        'date_created': data.get('dateCreated') or data.get('date_created') or '',
    }


def service_booking_from_frontend(data):
    return {
        'booking_id': data['bookingId'],
        'name': data.get('name') or '',
        'phone': data.get('phone') or '',
        'email': data.get('email') or '',
        'service': data.get('service') or '',
        'date': data.get('date') or '',
        'slot': data.get('slot') or '',
        'desc': data.get('desc') or '',
        'promo_code': data.get('promoCode') or '',
        'discount_applied': _dec(data.get('discountApplied')),
    }


def shop_settings_from_frontend(data):
    return {
        'name': data.get('name', SiteSettingsDefaults.name),
        'addr1': data.get('addr1', SiteSettingsDefaults.addr1),
        'addr2': data.get('addr2', SiteSettingsDefaults.addr2),
        'gst': data.get('gst', SiteSettingsDefaults.gst),
        'email': data.get('email', SiteSettingsDefaults.email),
        'phone': data.get('phone', SiteSettingsDefaults.phone),
        'products_catalog_cleared': bool(data.get('products_catalog_cleared')),
    }


class SiteSettingsDefaults:
    name = 'Jalaram Computers & IT Solutions'
    addr1 = 'Shop No. 5-7, Jalaram Arcade, Lamington Road'
    addr2 = 'Mumbai, Maharashtra - 400007'
    gst = '27AACJC2026P1Z3'
    email = 'jalaramcomputers21@gmail.com'
    phone = '+91 98928 48643'
