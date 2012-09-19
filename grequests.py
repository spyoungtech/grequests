# -*- coding: utf-8 -*-

"""
grequests
~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by gevent. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""

try:
    import gevent
    from gevent import monkey as curious_george
    from gevent.pool import Pool
except ImportError:
    raise RuntimeError('Gevent is required for grequests.')

# Monkey-patch.
curious_george.patch_all(thread=False, select=False)

from requests import api


__all__ = (
    'map', 'imap',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request'
)


def _greenlet_report_error(self, exc_info):
    import sys
    import traceback

    exception = exc_info[1]
    if isinstance(exception, gevent.greenlet.GreenletExit):
        self._report_result(exception)
        return
    exc_handler = False
    for lnk in self._links:
        if isinstance(lnk, gevent.greenlet.FailureSpawnedLink):
            exc_handler = True
            break
    if not exc_handler:
        try:
            traceback.print_exception(*exc_info)
        except:
            pass
    self._exception = exception
    if self._links and self._notifier is None:
        self._notifier = gevent.greenlet.core.active_event(self._notify_links)
    ## Only print errors
    if not exc_handler:
        info = str(self) + ' failed with '
        try:
            info += self._exception.__class__.__name__
        except Exception:
            info += str(self._exception) or repr(self._exception)
        sys.stderr.write(info + '\n\n')


## Patch the greenlet error reporting
gevent.greenlet.Greenlet._report_error = _greenlet_report_error


def patched(f):
    """Patches a given API function to not send."""

    def wrapped(*args, **kwargs):

        kwargs['return_response'] = False
        kwargs['prefetch'] = True

        config = kwargs.get('config', {})
        config.update(safe_mode=True)

        kwargs['config'] = config

        return f(*args, **kwargs)

    return wrapped


def send(r, pool=None, prefetch=False, exception_handler=None):
    """Sends the request object using the specified pool. If a pool isn't
    specified this method blocks. Pools are useful because you can specify size
    and can hence limit concurrency."""

    if pool != None:
        p = pool.spawn
    else:
        p = gevent.spawn

    if exception_handler:
        glet = p(r.send, prefetch=prefetch)

        def eh_wrapper(g):
            return exception_handler(r,g.exception)

        glet.link_exception(eh_wrapper)
    else:
        glet = p(r.send, prefetch=prefetch)

    return glet


# Patched requests.api functions.
get = patched(api.get)
options = patched(api.options)
head = patched(api.head)
post = patched(api.post)
put = patched(api.put)
patch = patched(api.patch)
delete = patched(api.delete)
request = patched(api.request)


def map(requests, prefetch=True, size=None, exception_handler=None):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param prefetch: If False, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. If None, no throttling occurs.
    """

    requests = list(requests)

    pool = Pool(size) if size else None
    jobs = [send(r, pool, prefetch=prefetch, exception_handler=exception_handler) for r in requests]
    gevent.joinall(jobs)

    return [r.response for r in requests]


def imap(requests, prefetch=True, size=2, exception_handler=None):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param prefetch: If False, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. default is 2
    """

    pool = Pool(size)

    def send(r):
        r.send(prefetch,exception_handler=exception_handler)
        return r.response

    for r in pool.imap_unordered(send, requests):
        yield r

    pool.join()
