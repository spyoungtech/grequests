#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Path hack
import os, sys
sys.path.insert(0, os.path.abspath('..'))

import time
import unittest

import erequests


HTTPBIN_URL = os.environ.get('HTTPBIN_URL', 'http://httpbin.org/')

def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""
    return HTTPBIN_URL + '/'.join(suffix)


N = 5
URLS = [httpbin('get?p=%s' % i) for i in range(N)]


class GrequestsCase(unittest.TestCase):

    def test_map(self):
        reqs = [erequests.get(url) for url in URLS]
        resp = erequests.map(reqs, size=N)
        self.assertEqual([r.url for r in resp], URLS)

    def test_imap(self):
        reqs = (erequests.get(url) for url in URLS)
        i = 0
        for i, r in enumerate(erequests.imap(reqs, size=N)):
            self.assertTrue(r.url in URLS)
        self.assertEqual(i, N - 1)

    def test_hooks(self):
        result = {}

        def hook(r, **kwargs):
            result[r.url] = True
            return r

        reqs = [erequests.get(url, hooks={'response': [hook]}) for url in URLS]
        resp = erequests.map(reqs, size=N)
        self.assertEqual(sorted(result.keys()), sorted(URLS))

    def test_callback_kwarg(self):
        result = {'ok': False}

        def callback(r, **kwargs):
            result['ok'] = True
            return r

        self.get(URLS[0], callback=callback)
        self.assertTrue(result['ok'])

    def test_session_and_cookies(self):
        c1 = {'k1': 'v1'}
        r = self.get(httpbin('cookies/set'), params=c1).json()
        self.assertEqual(r['cookies'], c1)
        s = erequests.Session()
        r = self.get(httpbin('cookies/set'), session=s, params=c1).json()
        self.assertEqual(dict(s.cookies), c1)

        # ensure all cookies saved
        c2 = {'k2': 'v2'}
        c1.update(c2)
        r = self.get(httpbin('cookies/set'), session=s, params=c2).json()
        self.assertEqual(dict(s.cookies), c1)

        # ensure new session is created
        r = self.get(httpbin('cookies')).json()
        self.assertEqual(r['cookies'], {})

        # cookies as param
        c3 = {'p1': '42'}
        r = self.get(httpbin('cookies'), cookies=c3).json()
        self.assertEqual(r['cookies'], c3)

    def test_calling_request(self):
        reqs = [erequests.request('POST', httpbin('post'), data={'p': i})
                for i in range(N)]
        resp = erequests.map(reqs, size=N)
        self.assertEqual([int(r.json()['form']['p']) for r in resp], list(range(N)))

    def test_stream_enabled(self):
        r = erequests.map([erequests.get(httpbin('stream/10'))],
                          size=2, stream=True)[0]
        self.assertFalse(r._content_consumed)

    def test_concurrency_with_delayed_url(self):
        t = time.time()
        n = 10
        reqs = [erequests.get(httpbin('delay/1')) for _ in range(n)]
        resp = erequests.map(reqs, size=n)
        self.assertLess((time.time() - t), n)

    def get(self, url, **kwargs):
        return erequests.map([erequests.get(url, **kwargs)])[0]


if __name__ == '__main__':
    unittest.main()

