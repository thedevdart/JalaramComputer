"""Phase 2 smoke test — content pages + form APIs."""
import json
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

BASE = 'http://127.0.0.1:8000'


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
    pages = ['/services', '/book-service', '/about', '/contact']
    for p in pages:
        code, html = s.request(p)
        assert code == 200, f'{p} returned {code}'
        assert 'jc-header' in html, f'{p} missing header'
    print('Pages: all 200')

    s.request('/contact')
    assert s.csrf(), 'missing csrftoken'

    code, body = s.request('/api/queries/', 'POST', {
        'name': 'Phase Two Test',
        'email': 'phase2@example.com',
        'phone': '+919892848643',
        'category': 'Laptop/PC Repair',
        'message': 'Test query from Phase 2 smoke test.',
        'date': '21 June 2026',
        'status': 'Open',
    }, csrf=True)
    assert code == 200, f'contact failed: {code} {body[:200]}'
    ticket = json.loads(body)['query']['ticketId']
    print('Contact query: OK (%s)' % ticket)

    code, body = s.request('/api/service-bookings/', 'POST', {
        'name': 'Phase Two Test',
        'phone': '+919892848643',
        'email': 'phase2@example.com',
        'service': 'Computer Repair',
        'date': '2026-06-25',
        'slot': 'Morning (09:00 AM - 12:00 PM)',
        'desc': 'Smoke test booking.',
        'promoCode': 'FIXNOW',
        'discountApplied': 500,
    }, csrf=True)
    assert code == 200, f'booking failed: {code} {body[:200]}'
    booking_id = json.loads(body)['booking']['bookingId']
    print('Service booking: OK (%s)' % booking_id)

    print('Phase 2 smoke test: ALL PASSED')


if __name__ == '__main__':
    main()
