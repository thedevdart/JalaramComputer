"""Storefront JSON API.

Only the endpoints the public site uses live here. All staff/store management
happens through the Django admin (shop/admin.py), so there is no admin JSON
surface to secure or maintain.
"""
import json
import logging
import re
import secrets

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .google_auth import verify_google_id_token
from .google_oauth import exchange_auth_code, get_user_info, redirect_uri
from .models import (
    ContactQuery,
    HeroSlideConfig,
    NewsletterSubscriber,
    Order,
    Product,
    ServiceBooking,
    SiteSettings,
)
from .serializers import order_from_frontend, service_booking_from_frontend

UserModel = get_user_model()
EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
logger = logging.getLogger(__name__)


def _unique_username(base: str) -> str:
    username = re.sub(r'[^a-zA-Z0-9_]', '', base)[:30] or 'user'
    candidate = username
    n = 1
    while UserModel.objects.filter(username=candidate).exists():
        candidate = f'{username}{n}'
        n += 1
    return candidate


def _apply_google_name(user, idinfo: dict):
    given = (idinfo.get('given_name') or '').strip()
    family = (idinfo.get('family_name') or '').strip()
    full = (idinfo.get('name') or '').strip()
    if not user.get_full_name() and (given or full):
        if given:
            user.first_name = given
            user.last_name = family
        elif full:
            parts = full.split(' ', 1)
            user.first_name = parts[0]
            user.last_name = parts[1] if len(parts) > 1 else ''
        user.save(update_fields=['first_name', 'last_name'])


def _get_or_create_google_user(email: str, idinfo: dict):
    user = UserModel.objects.filter(email__iexact=email).first()
    if user:
        _apply_google_name(user, idinfo)
        return user

    username = _unique_username(email.split('@')[0])
    user = UserModel.objects.create_user(username=username, email=email)
    user.set_unusable_password()
    _apply_google_name(user, idinfo)
    user.save()
    return user


def _json_body(request):
    try:
        return json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return {}


def _send_order_confirmation(order):
    """Send a plain-text order confirmation to the customer. Best-effort — never raises."""
    email = (order.customer.get('email') or '').strip()
    if not email or not getattr(settings, 'EMAIL_HOST_USER', ''):
        return

    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    shop_name = getattr(settings, 'SHOP_NAME', 'Jalaram Computers')
    shop_email = getattr(settings, 'SHOP_EMAIL', '')
    shop_phone = getattr(settings, 'SHOP_PHONE', '')
    name = order.customer.get('name') or 'Customer'

    items_text = '\n'.join(
        f"  • {it.get('name', 'Item')} × {it.get('quantity', 1)}"
        f"  —  ₹{float(it.get('price', 0)) * int(it.get('quantity', 1)):,.0f}"
        for it in (order.items or [])
    )

    body = (
        f"Hi {name},\n\n"
        f"Thank you for your order with {shop_name}!\n\n"
        f"Order Number : {order.order_id}\n"
        f"Date         : {order.date}\n"
        f"Payment      : {order.payment_method}\n\n"
        f"Items:\n{items_text}\n\n"
        f"Subtotal  : ₹{float(order.subtotal):,.2f}\n"
        f"GST (18%) : ₹{float(order.gst):,.2f}\n"
        f"Total     : ₹{float(order.total):,.2f}\n\n"
        f"Track your order: {site_url}/order-confirmed?id={order.order_id}\n\n"
        f"Questions? Reach us at {shop_email} or {shop_phone}.\n\n"
        f"Thank you for choosing {shop_name}!"
    )

    try:
        send_mail(
            subject=f"Order {order.order_id} Confirmed — {shop_name}",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exc:
        logger.error('Order confirmation email failed for %s (order %s): %s', email, order.order_id, exc)


def _is_staff_user(user):
    if not user or not user.is_authenticated:
        return False
    admin_email = getattr(settings, 'ADMIN_EMAIL', '').lower()
    if admin_email and user.email.lower() == admin_email:
        return True
    return user.is_staff


def _user_payload(user):
    if not user or not user.is_authenticated:
        return None
    return {
        'uid': str(user.pk),
        'email': user.email,
        'displayName': user.get_full_name() or user.username,
        'emailVerified': True,
        'isStaff': _is_staff_user(user),
    }


# ── Auth ────────────────────────────────────────────────────────────────────

def _login_with_google_idinfo(request, idinfo: dict):
    """Create or fetch a user from verified Google claims, then log them in."""
    email = (idinfo.get('email') or '').strip().lower()
    if not email or not EMAIL_RE.match(email):
        raise ValueError('Google account has no usable email.')
    if not idinfo.get('email_verified'):
        raise ValueError('Please verify your Google email first.')
    user = _get_or_create_google_user(email, idinfo)
    login(request, user)
    return user


def _login_with_google_credential(request, credential: str):
    client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
    if not client_id:
        raise ValueError('Google sign-in is not configured yet.')

    try:
        idinfo = verify_google_id_token(credential, client_id)
    except ValueError as exc:
        logger.warning('Google ID token verify failed: %s', exc)
        raise ValueError('verify_failed') from exc

    return _login_with_google_idinfo(request, idinfo)


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
    if UserModel.objects.filter(email__iexact=email).exists():
        return JsonResponse({'ok': False, 'error': 'An account with this email already exists.'}, status=400)

    try:
        validate_password(password)
    except DjangoValidationError as exc:
        return JsonResponse({'ok': False, 'error': exc.messages[0]}, status=400)

    username = _unique_username(email.split('@')[0])

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
        if not user.has_usable_password():
            return JsonResponse({
                'ok': False,
                'error': 'This account uses Google sign-in. Use Continue with Google below.',
            }, status=401)
        return JsonResponse({'ok': False, 'error': 'Invalid email or password.'}, status=401)

    login(request, authed)
    return JsonResponse({'ok': True, 'user': _user_payload(authed)})


@require_POST
def auth_logout(request):
    logout(request)
    return JsonResponse({'ok': True})


@require_GET
def auth_config(request):
    client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '') or None
    redirect = redirect_uri(request) if client_id else None
    return JsonResponse({'googleClientId': client_id, 'redirectUri': redirect})


@require_POST
def auth_google(request):
    client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
    if not client_id:
        return JsonResponse({'ok': False, 'error': 'Google sign-in is not configured yet.'}, status=503)

    data = _json_body(request)
    credential = (data.get('credential') or data.get('idToken') or '').strip()
    if not credential:
        return JsonResponse({'ok': False, 'error': 'Missing Google credential.'}, status=400)

    try:
        user = _login_with_google_credential(request, credential)
    except ValueError as exc:
        return JsonResponse({'ok': False, 'error': str(exc) or 'Google sign-in could not be verified.'}, status=401)

    return JsonResponse({'ok': True, 'user': _user_payload(user)})


@csrf_exempt
def auth_google_callback(request):
    """OAuth code flow (GET) or legacy GIS credential POST."""
    if request.method == 'GET':
        if request.GET.get('error'):
            return redirect('/account?google_error=denied')

        state = (request.GET.get('state') or '').strip()
        expected = request.session.pop('google_oauth_state', None)
        if not state or not expected or state != expected:
            return redirect('/account?google_error=csrf')

        code = (request.GET.get('code') or '').strip()
        if not code:
            return redirect('/account?google_error=missing')

        oauth_redirect_uri = request.session.pop('google_oauth_redirect_uri', None) or redirect_uri(request)

        try:
            tokens = exchange_auth_code(code, oauth_redirect_uri)
            access_token = (tokens.get('access_token') or '').strip()
            if not access_token:
                logger.warning('Google token response missing access_token: %s', list(tokens.keys()))
                return redirect('/account?google_error=token')
            idinfo = get_user_info(access_token)
            _login_with_google_idinfo(request, idinfo)
            request.session.save()
        except ValueError as exc:
            logger.warning('Google OAuth callback failed: %s', exc)
            reason = str(exc).split(':', 1)[0]
            if reason in ('token_http', 'token', 'token_network', 'secret_missing',
                          'userinfo_http', 'userinfo_network'):
                return redirect('/account?google_error=token')
            return redirect('/account?google_error=invalid')

        return redirect('/account')

    if request.method == 'POST':
        credential = (request.POST.get('credential') or '').strip()
        if not credential:
            return redirect('/account?google_error=missing')

        csrf = (request.POST.get('g_csrf_token') or '').strip()
        cookie_csrf = (request.COOKIES.get('g_csrf_token') or '').strip()
        if csrf and cookie_csrf and csrf != cookie_csrf:
            return redirect('/account?google_error=csrf')

        try:
            _login_with_google_credential(request, credential)
        except ValueError:
            return redirect('/account?google_error=invalid')

        return redirect('/account')

    return redirect('/account?google_error=missing')


# ── Catalog & settings (read-only) ──────────────────────────────────────────

@require_GET
def products_list(request):
    return JsonResponse([p.to_frontend() for p in Product.objects.all()], safe=False)


@require_GET
def products_detail(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Not found.'}, status=404)
    return JsonResponse(product.to_frontend())


@require_GET
def settings_shop(request):
    return JsonResponse(SiteSettings.load().to_frontend())


def _hero_slides_fallback():
    path = settings.BASE_DIR / 'public' / 'data' / 'hero-services.json'
    if path.exists():
        with open(path, encoding='utf-8') as f:
            return JsonResponse(json.load(f))
    return JsonResponse({'autoPlayMs': 4500, 'slides': []})


@require_GET
def settings_hero_slides(request):
    config = HeroSlideConfig.load()
    if not config.slides:
        return _hero_slides_fallback()
    return JsonResponse(config.to_frontend())


# ── Orders ──────────────────────────────────────────────────────────────────

def _generate_order_id():
    year = timezone.now().year
    for _ in range(25):
        oid = f'JC-{year}-{secrets.randbelow(900000) + 100000}'
        if not Order.objects.filter(order_id=oid).exists():
            return oid
    return f'JC-{year}-{secrets.token_hex(4).upper()}'


@require_http_methods(['GET', 'POST'])
def orders_collection(request):
    if request.method == 'GET':
        if _is_staff_user(request.user):
            return JsonResponse([o.to_frontend() for o in Order.objects.all()], safe=False)
        if not request.user.is_authenticated:
            return JsonResponse([], safe=False)
        email = request.user.email.lower()
        seen = set()
        orders = []
        for o in Order.objects.filter(user=request.user):
            seen.add(o.order_id)
            orders.append(o.to_frontend())
        for o in Order.objects.filter(user_id_str=str(request.user.pk)).exclude(order_id__in=seen):
            seen.add(o.order_id)
            orders.append(o.to_frontend())
        if email:
            for o in Order.objects.filter(customer__email__iexact=email).exclude(order_id__in=seen):
                seen.add(o.order_id)
                orders.append(o.to_frontend())
        return JsonResponse(orders, safe=False)

    # POST — create an order. The order id is generated server-side so a client
    # cannot overwrite an existing order by supplying its id.
    data = _json_body(request)
    if not data.get('items'):
        return JsonResponse({'ok': False, 'error': 'Cart is empty.'}, status=400)
    user = request.user if request.user.is_authenticated else None
    if user and not data.get('userId'):
        data['userId'] = str(user.pk)
    data['orderId'] = _generate_order_id()
    fields = order_from_frontend(data, user=user)
    order = Order.objects.create(**fields)
    _send_order_confirmation(order)
    return JsonResponse({'ok': True, 'order': order.to_frontend()})


@require_GET
def orders_detail(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Not found.'}, status=404)
    return JsonResponse(order.to_frontend())


# ── Customer-submitted forms ────────────────────────────────────────────────

@require_POST
def queries_create(request):
    data = _json_body(request)
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip().lower()
    message = (data.get('message') or '').strip()

    if not name:
        return JsonResponse({'ok': False, 'error': 'Name is required.'}, status=400)
    if not EMAIL_RE.match(email):
        return JsonResponse({'ok': False, 'error': 'A valid email address is required.'}, status=400)
    if not message:
        return JsonResponse({'ok': False, 'error': 'Message is required.'}, status=400)

    ticket_id = data.get('ticketId') or f'JLR-QTK-{ContactQuery.objects.count() + 100000}'
    obj = ContactQuery.objects.create(
        ticket_id=ticket_id,
        name=name,
        email=email,
        phone=(data.get('phone') or '').strip(),
        category=(data.get('category') or '').strip(),
        message=message,
        date=data.get('date', ''),
        status='Open',
    )
    return JsonResponse({'ok': True, 'query': obj.to_frontend()})


@require_POST
def service_bookings_create(request):
    data = _json_body(request)
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()
    email = (data.get('email') or '').strip().lower()
    service = (data.get('service') or '').strip()
    date = (data.get('date') or '').strip()
    slot = (data.get('slot') or '').strip()
    desc = (data.get('desc') or '').strip()

    if not name:
        return JsonResponse({'ok': False, 'error': 'Name is required.'}, status=400)
    if not EMAIL_RE.match(email):
        return JsonResponse({'ok': False, 'error': 'A valid email address is required.'}, status=400)
    if not service:
        return JsonResponse({'ok': False, 'error': 'Service type is required.'}, status=400)
    if not date:
        return JsonResponse({'ok': False, 'error': 'Appointment date is required.'}, status=400)
    if not slot:
        return JsonResponse({'ok': False, 'error': 'Time slot is required.'}, status=400)
    if not desc:
        return JsonResponse({'ok': False, 'error': 'Please describe your issue.'}, status=400)

    data['bookingId'] = data.get('bookingId') or f'BK-{ServiceBooking.objects.count() + 100000}'
    fields = service_booking_from_frontend(data)
    obj = ServiceBooking.objects.create(**fields)
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
        # Subscription is recorded; the welcome email is best-effort.
        return JsonResponse({
            'ok': True,
            'message': 'Thanks for subscribing! You are on the list.',
        })

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
    except Exception as exc:
        logger.error('Newsletter welcome email failed for %s: %s', email, exc)
        return JsonResponse({
            'ok': True,
            'message': 'Thanks for subscribing! You are on the list.',
        })

    return JsonResponse({
        'ok': True,
        'message': 'Welcome to the family! Check your inbox for a confirmation email.',
    })
