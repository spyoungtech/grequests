#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Path hack
import os, sys
sys.path.insert(0, os.path.abspath('..'))

import time
import unittest

import requests
import grequests

HTTPBIN_URL = os.environ.get('HTTPBIN_URL', 'http://httpbin.org/')

def httpbin(*suffix):
    """Returns url for HTTPBIN resource."""
    return HTTPBIN_URL + '/'.join(suffix)


N = 5
URLS = [httpbin('get?p=%s' % i) for i in range(N)]


class GrequestsCase(unittest.TestCase):

    def test_map(self):
        reqs = [grequests.get(url) for url in URLS]
        resp = grequests.map(reqs, size=N)
        self.assertEqual([r.url for r in resp], URLS)

    def test_imap(self):
        reqs = (grequests.get(url) for url in URLS)
        i = 0
        for i, r in enumerate(grequests.imap(reqs, size=N)):
            self.assertTrue(r.url in URLS)
        self.assertEqual(i, N - 1)

    def test_hooks(self):
        result = {}

        def hook(r, **kwargs):
            result[r.url] = True
            return r

        reqs = [grequests.get(url, hooks={'response': [hook]}) for url in URLS]
        grequests.map(reqs, size=N)
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
        s = requests.Session()
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
        reqs = [grequests.request('POST', httpbin('post'), data={'p': i})
                for i in range(N)]
        resp = grequests.map(reqs, size=N)
        self.assertEqual([int(r.json()['form']['p']) for r in resp], list(range(N)))

    def test_stream_enabled(self):
        r = grequests.map([grequests.get(httpbin('stream/10'))],
                          size=2, stream=True)[0]
        self.assertFalse(r._content_consumed)

    def test_concurrency_with_delayed_url(self):
        t = time.time()
        n = 10
        reqs = [grequests.get(httpbin('delay/1')) for _ in range(n)]
        grequests.map(reqs, size=n)
        self.assertLess((time.time() - t), n)

    def test_map_timeout(self):
        reqs = [grequests.get(httpbin('delay/1'), timeout=0.001), grequests.get(httpbin('/'))]
        responses = grequests.map(reqs)
        self.assertEqual(len(responses), 1)

    def test_imap_timeout(self):
        reqs = [grequests.get(httpbin('delay/1'), timeout=0.001), grequests.get(httpbin('/'))]
        responses = list(grequests.imap(reqs))
        self.assertEqual(len(responses), 1)

    def test_map_timeout_exception(self):
        class ExceptionHandler:
            def __init__(self):
                self.counter = 0

            def callback(self, request, exception):
                 self.counter += 1
        eh = ExceptionHandler()
        reqs = [grequests.get(httpbin('delay/1'), timeout=0.001)]
        list(grequests.map(reqs, exception_handler=eh.callback))
        self.assertEqual(eh.counter, 1)

    def test_imap_timeout_exception(self):
        class ExceptionHandler:
            def __init__(self):
                self.counter = 0

            def callback(self, request, exception):
                 self.counter += 1
        eh = ExceptionHandler()
        reqs = [grequests.get(httpbin('delay/1'), timeout=0.001)]
        list(grequests.imap(reqs, exception_handler=eh.callback))
        self.assertEqual(eh.counter, 1)

    def get(self, url, **kwargs):
        return grequests.map([grequests.get(url, **kwargs)])[0]


if __name__ == '__main__':
    unittest.main()
