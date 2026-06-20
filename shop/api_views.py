import json
import re

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

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
from .serializers import (
    order_from_frontend,
    product_from_frontend,
    service_booking_from_frontend,
    service_request_from_frontend,
    shop_settings_from_frontend,
)

UserModel = get_user_model()
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


def _user_payload(user):
    if not user or not user.is_authenticated:
        return None
    return {
        'uid': str(user.pk),
        'email': user.email,
        'displayName': user.get_full_name() or user.username,
        'emailVerified': True,
    }


def _is_staff_user(user):
    if not user or not user.is_authenticated:
        return False
    admin_email = getattr(settings, 'ADMIN_EMAIL', '').lower()
    if admin_email and user.email.lower() == admin_email:
        return True
    return user.is_staff


def _require_staff(request):
    if not _is_staff_user(request.user):
        return JsonResponse({'ok': False, 'error': 'Admin access required.'}, status=403)
    return None


@require_GET
def auth_me(request):
    return JsonResponse({'user': _user_payload(request.user)})


@require_POST
def auth_register(request):
    data = _json_body(request)
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    full_name = (data.get('fullName') or data.get('full_name') or '').strip()

    if not EMAIL_RE.match(email):
        return JsonResponse({'ok': False, 'error': 'Invalid email.'}, status=400)
    if len(password) < 6:
        return JsonResponse({'ok': False, 'error': 'Password must be at least 6 characters.'}, status=400)
    if UserModel.objects.filter(email__iexact=email).exists():
        return JsonResponse({'ok': False, 'error': 'An account with this email already exists.'}, status=400)

    username = email.split('@')[0]
    base = username
    n = 1
    while UserModel.objects.filter(username=username).exists():
        username = f'{base}{n}'
        n += 1

    user = UserModel.objects.create_user(username=username, email=email, password=password)
    if full_name:
        parts = full_name.split(' ', 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''
        user.save(update_fields=['first_name', 'last_name'])

    login(request, user)
    return JsonResponse({'ok': True, 'user': _user_payload(user)})


@require_POST
def auth_login(request):
    data = _json_body(request)
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    user = UserModel.objects.filter(email__iexact=email).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'Invalid email or password.'}, status=401)

    authed = authenticate(request, username=user.username, password=password)
    if not authed:
        return JsonResponse({'ok': False, 'error': 'Invalid email or password.'}, status=401)

    login(request, authed)
    return JsonResponse({'ok': True, 'user': _user_payload(authed)})


@require_POST
def auth_logout(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_POST
def admin_login(request):
    """Staff login for admin dashboard (username or email + password)."""
    data = _json_body(request)
    identifier = (data.get('username') or data.get('email') or '').strip()
    password = data.get('password') or ''

    user = UserModel.objects.filter(username=identifier).first()
    if not user and '@' in identifier:
        user = UserModel.objects.filter(email__iexact=identifier).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'Invalid credentials.'}, status=401)

    authed = authenticate(request, username=user.username, password=password)
    if not authed or not _is_staff_user(authed):
        return JsonResponse({'ok': False, 'error': 'Invalid credentials.'}, status=401)

    login(request, authed)
    return JsonResponse({'ok': True, 'user': _user_payload(authed), 'isStaff': True})


@require_GET
def products_list(request):
    products = [p.to_frontend() for p in Product.objects.all()]
    return JsonResponse(products, safe=False)


@require_http_methods(['GET', 'PUT', 'POST', 'DELETE'])
def products_detail(request, product_id):
    denied = _require_staff(request)
    if request.method != 'GET' and denied:
        return denied

    if request.method == 'GET':
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Not found.'}, status=404)
        return JsonResponse(product.to_frontend())

    if request.method == 'DELETE':
        Product.objects.filter(pk=product_id).delete()
        return JsonResponse({'ok': True})

    data = _json_body(request)
    if request.method == 'POST' and not data.get('id'):
        data['id'] = product_id
    fields = product_from_frontend(data)
    product, _ = Product.objects.update_or_create(slug=fields.pop('slug'), defaults=fields)
    return JsonResponse({'ok': True, 'product': product.to_frontend()})


@require_GET
def settings_shop(request):
    return JsonResponse(SiteSettings.load().to_frontend())


@require_http_methods(['GET', 'PUT'])
def settings_shop_admin(request):
    if request.method == 'GET':
        return JsonResponse(SiteSettings.load().to_frontend())
    denied = _require_staff(request)
    if denied:
        return denied
    data = _json_body(request)
    settings_obj = SiteSettings.load()
    for key, val in shop_settings_from_frontend(data).items():
        setattr(settings_obj, key, val)
    settings_obj.save()
    return JsonResponse({'ok': True, 'settings': settings_obj.to_frontend()})


@require_GET
def settings_hero_slides(request):
    config = HeroSlideConfig.load()
    if not config.slides:
        return _hero_slides_fallback()
    return JsonResponse(config.to_frontend())


def _hero_slides_fallback():
    from pathlib import Path

    path = settings.BASE_DIR / 'public' / 'data' / 'hero-services.json'
    if path.exists():
        with open(path, encoding='utf-8') as f:
            return JsonResponse(json.load(f))
    return JsonResponse({'autoPlayMs': 4500, 'slides': []})


@require_http_methods(['GET', 'PUT'])
def settings_hero_admin(request):
    if request.method == 'GET':
        config = HeroSlideConfig.load()
        if config.slides:
            return JsonResponse(config.to_frontend())
        return _hero_slides_fallback()
    denied = _require_staff(request)
    if denied:
        return denied
    data = _json_body(request)
    config = HeroSlideConfig.load()
    config.auto_play_ms = int(data.get('autoPlayMs') or 4500)
    config.slides = data.get('slides') or []
    config.save()
    return JsonResponse({'ok': True, 'config': config.to_frontend()})


@require_http_methods(['GET', 'POST'])
def orders_collection(request):
    if request.method == 'GET':
        if _is_staff_user(request.user):
            orders = [o.to_frontend() for o in Order.objects.all()]
            return JsonResponse(orders, safe=False)
        if not request.user.is_authenticated:
            return JsonResponse([], safe=False)
        email = request.user.email.lower()
        seen = set()
        orders = []
        for o in Order.objects.filter(user=request.user):
            if o.order_id not in seen:
                seen.add(o.order_id)
                orders.append(o.to_frontend())
        for o in Order.objects.filter(user_id_str=str(request.user.pk)):
            if o.order_id not in seen:
                seen.add(o.order_id)
                orders.append(o.to_frontend())
        for o in Order.objects.all():
            customer_email = (o.customer or {}).get('email', '').lower()
            if customer_email == email and o.order_id not in seen:
                seen.add(o.order_id)
                orders.append(o.to_frontend())
        return JsonResponse(orders, safe=False)

    data = _json_body(request)
    if not data.get('orderId'):
        return JsonResponse({'ok': False, 'error': 'orderId required.'}, status=400)

    user = request.user if request.user.is_authenticated else None
    if user and not data.get('userId'):
        data['userId'] = str(user.pk)

    fields = order_from_frontend(data, user=user)
    order_id = fields.pop('order_id')
    order, _ = Order.objects.update_or_create(order_id=order_id, defaults=fields)
    return JsonResponse({'ok': True, 'order': order.to_frontend()})


@require_http_methods(['GET', 'PUT', 'PATCH'])
def orders_detail(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Not found.'}, status=404)

    if request.method == 'GET':
        return JsonResponse(order.to_frontend())

    denied = _require_staff(request)
    if denied:
        return denied

    data = _json_body(request)
    merged = {**order.to_frontend(), **data}
    fields = order_from_frontend(merged, user=order.user)
    fields.pop('order_id')
    for key, val in fields.items():
        setattr(order, key, val)
    order.save()
    return JsonResponse({'ok': True, 'order': order.to_frontend()})


@require_POST
def queries_create(request):
    data = _json_body(request)
    ticket_id = data.get('ticketId') or f'JLR-QTK-{ContactQuery.objects.count() + 100000}'
    obj = ContactQuery.objects.create(
        ticket_id=ticket_id,
        name=data.get('name', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        category=data.get('category', ''),
        message=data.get('message', ''),
        date=data.get('date', ''),
        status=data.get('status', 'Open'),
    )
    return JsonResponse({'ok': True, 'query': obj.to_frontend()})


@require_http_methods(['GET'])
def queries_list(request):
    denied = _require_staff(request)
    if denied:
        return denied
    queries = [q.to_frontend() for q in ContactQuery.objects.all()]
    return JsonResponse(queries, safe=False)


@require_http_methods(['GET', 'POST', 'PUT', 'DELETE'])
def services_collection(request):
    if request.method == 'GET':
        if not _is_staff_user(request.user):
            services = [s.to_frontend() for s in ServiceRequest.objects.all()]
            return JsonResponse(services, safe=False)
        services = [s.to_frontend() for s in ServiceRequest.objects.all()]
        return JsonResponse(services, safe=False)

    denied = _require_staff(request)
    if denied:
        return denied

    data = _json_body(request)
    request_id = data.get('requestId')
    if not request_id:
        return JsonResponse({'ok': False, 'error': 'requestId required.'}, status=400)

    fields = service_request_from_frontend(data)
    rid = fields.pop('request_id')
    obj, _ = ServiceRequest.objects.update_or_create(request_id=rid, defaults=fields)
    return JsonResponse({'ok': True, 'service': obj.to_frontend()})


@require_http_methods(['DELETE'])
def services_detail(request, request_id):
    denied = _require_staff(request)
    if denied:
        return denied
    ServiceRequest.objects.filter(request_id=request_id).delete()
    return JsonResponse({'ok': True})


@require_POST
def service_bookings_create(request):
    data = _json_body(request)
    booking_id = data.get('bookingId') or f'BK-{ServiceBooking.objects.count() + 100000}'
    data['bookingId'] = booking_id
    fields = service_booking_from_frontend(data)
    bid = fields.pop('booking_id')
    obj, _ = ServiceBooking.objects.update_or_create(booking_id=bid, defaults=fields)
    return JsonResponse({'ok': True, 'booking': obj.to_frontend()})


@require_POST
def newsletter_subscribe(request):
    data = _json_body(request)
    email = (data.get('email') or '').strip().lower()
    if not EMAIL_RE.match(email):
        return JsonResponse({'ok': False, 'error': 'Please enter a valid email address.'}, status=400)

    subscriber, is_new = NewsletterSubscriber.objects.get_or_create(email=email)
    if not is_new:
        return JsonResponse({
            'ok': True,
            'alreadySubscribed': True,
            'message': 'You are already subscribed to our newsletter.',
        })

    if not settings.EMAIL_HOST_USER:
        return JsonResponse({
            'ok': False,
            'error': 'Email is not configured yet. Add SMTP settings to the server environment.',
        }, status=503)

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    shop_name = getattr(settings, 'SHOP_NAME', 'Jalaram Computers')
    try:
        send_mail(
            subject=f'Welcome to {shop_name}!',
            message=f'Thank you for subscribing to our newsletter.\n\nVisit us at {site_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception:
        subscriber.delete()
        return JsonResponse({
            'ok': False,
            'error': 'Could not send the welcome email. Please try again in a moment.',
        }, status=500)

    return JsonResponse({
        'ok': True,
        'message': 'Welcome to the family! Check your inbox for a confirmation email.',
    })


@require_POST
def admin_bulk_sync(request):
    """Accept bulk sync payload from admin localStorage."""
    denied = _require_staff(request)
    if denied:
        return denied

    data = _json_body(request)

    if 'products' in data:
        for item in data['products']:
            fields = product_from_frontend(item)
            Product.objects.update_or_create(slug=fields.pop('slug'), defaults=fields)

    if 'orders' in data:
        for item in data['orders']:
            fields = order_from_frontend(item)
            oid = fields.pop('order_id')
            Order.objects.update_or_create(order_id=oid, defaults=fields)

    if 'services' in data:
        for item in data['services']:
            fields = service_request_from_frontend(item)
            rid = fields.pop('request_id')
            ServiceRequest.objects.update_or_create(request_id=rid, defaults=fields)

    if 'shopDetails' in data:
        settings_obj = SiteSettings.load()
        for key, val in shop_settings_from_frontend(data['shopDetails']).items():
            setattr(settings_obj, key, val)
        settings_obj.save()

    return JsonResponse({'ok': True})


@require_POST
def admin_clear_products(request):
    denied = _require_staff(request)
    if denied:
        return denied
    Product.objects.all().delete()
    settings_obj = SiteSettings.load()
    settings_obj.products_catalog_cleared = True
    settings_obj.save()
    return JsonResponse({'ok': True})
