"""Phase 1 smoke test — pages + auth + order flow."""
import json
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

BASE = 'http://127.0.0.1:8000'
EMAIL = 'phase1test@example.com'
PASSWORD = 'testpass123'
ORDER_ID = 'JC-2026-9999'


class Session:
    def __init__(self):
        self.jar = CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def csrf(self):
        for c in self.jar:
            if c.name == 'csrftoken':
                return c.value
        return ''

    def request(self, path, method='GET', data=None, csrf=False):
        headers = {'Content-Type': 'application/json'}
        if csrf:
            token = self.csrf()
            if token:
                headers['X-CSRFToken'] = token
        body = json.dumps(data).encode() if data is not None else None
        req = urllib.request.Request(BASE + path, data=body, headers=headers, method=method)
        try:
            with self.opener.open(req, timeout=15) as resp:
                return resp.status, resp.read().decode()
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()


def main():
    s = Session()
    pages = ['/', '/shop', '/product', '/cart', '/checkout', '/order-confirmed', '/account']
    for p in pages:
        code, _ = s.request(p)
        assert code == 200, f'{p} returned {code}'
    print('Pages: all 200')

    s.request('/account')
    assert s.csrf(), 'missing csrftoken'

    code, body = s.request('/api/auth/register/', 'POST', {
        'email': EMAIL, 'password': PASSWORD, 'fullName': 'Phase One',
    }, csrf=True)
    if code == 400 and 'already exists' in body:
        code, body = s.request('/api/auth/login/', 'POST', {'email': EMAIL, 'password': PASSWORD}, csrf=True)
    assert code == 200, f'auth failed: {code} {body[:200]}'
    print('Auth: OK')

    code, body = s.request('/api/auth/me/')
    assert json.loads(body)['user']['email'] == EMAIL
    print('Auth me: OK')

    order = {
        'orderId': ORDER_ID,
        'date': '21 June 2026',
        'status': 'Processing',
        'paid': False,
        'subtotal': 1000,
        'discount': 0,
        'gst': 180,
        'total': 1180,
        'customer': {'name': 'Phase One', 'email': EMAIL, 'phone': '+919892848643'},
        'shippingDetails': {
            'address': 'Shop No. 5-7, Jalaram Arcade, Lamington Road',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400007',
            'method': 'Standard (5–7 days)',
        },
        'items': [{'id': 'test-1', 'name': 'Test Product', 'price': 1000, 'quantity': 1, 'imageIcon': 'lucide:box'}],
        'paymentMethod': 'Cash on Delivery',
    }
    code, body = s.request('/api/orders/', 'POST', order, csrf=True)
    assert code == 200, f'order save failed: {code} {body[:200]}'
    print('Save order: OK')

    code, body = s.request('/api/orders/')
    orders = json.loads(body)
    assert any(o.get('orderId') == ORDER_ID for o in orders)
    print('My orders: OK (%d)' % len(orders))

    code, body = s.request('/api/orders/%s/' % ORDER_ID)
    assert json.loads(body)['orderId'] == ORDER_ID
    print('Order detail: OK')

    code, _ = s.request('/api/auth/logout/', 'POST', {}, csrf=True)
    assert code == 200
    code, _ = s.request('/api/auth/login/', 'POST', {'email': EMAIL, 'password': PASSWORD}, csrf=True)
    assert code == 200
    print('Logout/login: OK')

    print('Phase 1 smoke test: ALL PASSED')


if __name__ == '__main__':
    main()
