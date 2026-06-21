"""Server-side Google OAuth 2.0 (authorization code flow). No GIS popup."""
import json
import urllib.request
from urllib import parse

from django.conf import settings

GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
GOOGLE_TOKEN_URL = 'https://oauth2.googleapis.com/token'
SCOPES = 'openid email profile'
CALLBACK_PATH = '/account/google/callback/'


def redirect_uri(request=None) -> str:
    """Must match Google Console → Authorized redirect URIs character-for-character."""
    explicit = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', '')
    if explicit:
        return explicit if explicit.endswith('/') else f'{explicit}/'

    site = (getattr(settings, 'SITE_URL', '') or '').rstrip('/')
    if site:
        return f'{site}{CALLBACK_PATH}'

    if request is not None:
        return request.build_absolute_uri(CALLBACK_PATH)

    return f'http://localhost:8000{CALLBACK_PATH}'


def start_url(request, state: str) -> str:
    uri = redirect_uri(request)
    params = {
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'redirect_uri': uri,
        'response_type': 'code',
        'scope': SCOPES,
        'state': state,
        'access_type': 'online',
        'prompt': 'select_account',
    }
    return f'{GOOGLE_AUTH_URL}?{parse.urlencode(params)}'


def exchange_auth_code(http_request, code: str) -> dict:
    secret = getattr(settings, 'GOOGLE_OAUTH_CLIENT_SECRET', '')
    if not secret:
        raise ValueError('Google OAuth client secret is not configured.')

    uri = redirect_uri(http_request)
    body = parse.urlencode({
        'code': code,
        'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
        'client_secret': secret,
        'redirect_uri': uri,
        'grant_type': 'authorization_code',
    }).encode()

    req = urllib.request.Request(GOOGLE_TOKEN_URL, data=body, method='POST')
    req.add_header('Content-Type', 'application/x-www-form-urlencoded')
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())
