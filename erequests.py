# -*- coding: utf-8 -*-

"""
erequests
~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by eventlet. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""

import eventlet

# Monkey-patch.
requests = eventlet.patcher.import_patched('requests')

__all__ = ['map', 'imap', 'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request']

# Export same items as vanilla requests
__requests_imports__ = ['utils', 'session', 'Session', 'codes', 'RequestException', 'Timeout', 'URLRequired', 'TooManyRedirects', 'HTTPError', 'ConnectionError']
eventlet.patcher.slurp_properties(requests, globals(), srckeys=__requests_imports__)
__all__.extend(__requests_imports__)
del requests, __requests_imports__


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response. Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, session=None):
        self.method = method
        self.url = url
        self.session = session or Session()
        self.response = None
        self._prepared_kwargs = None

    def prepare(self, **kwargs):
        assert self._prepared_kwargs is None, 'cannot call prepare multiple times'
        self._prepared_kwargs = kwargs

    def send(self, **kwargs):
        kw = self._prepared_kwargs or {}
        kw.update(kwargs)
        self.response = self.session.request(self.method, self.url, **kw)
        return self.response


def request(method, url, **kwargs):
    req = AsyncRequest(method, url)
    return eventlet.spawn(req.send, **kwargs).wait()


def get(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('GET', url, **kwargs)


def options(url, **kwargs):
    kwargs.setdefault('allow_redirects', True)
    return request('OPTIONS', url, **kwargs)


def head(url, **kwargs):
    kwargs.setdefault('allow_redirects', False)
    return request('HEAD', url, **kwargs)


def post(url, data=None, **kwargs):
    return request('POST', url, data=data, **kwargs)


def put(url, data=None, **kwargs):
    return request('PUT', url, data=data, **kwargs)


def patch(url, data=None, **kwargs):
    return request('PATCH', url, data=data, **kwargs)


def delete(url, **kwargs):
    return request('DELETE', url, **kwargs)


def map(requests, size=10):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param size: Specifies the number of requests to make at a time. If None, no throttling occurs.
    """

    results = []

    def send(r):
        try:
            results.append(r.send())
        except Exception as e:
            results.append(e)

    pool = eventlet.GreenPool(size)
    for r in requests:
        pool.spawn(send, r)
    pool.waitall()

    return results


def imap(requests, size=10):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param size: Specifies the number of requests to make at a time. default is 2
    """

    pool = eventlet.GreenPool(size)

    def send(r):
        try:
            return r.send()
        except Exception as e:
            return e

    for r in pool.imap(send, requests):
        yield r

    pool.waitall()

