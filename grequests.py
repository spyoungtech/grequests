# -*- coding: utf-8 -*-

"""
grequests
~~~~~~~~~

This module contains an asynchronous replica of ``requests.api``, powered
by gevent. All API methods return a ``Request`` instance (as opposed to
``Response``). A list of requests can be sent with ``map()``.
"""
from functools import partial
import traceback

try:
    import gevent
    from gevent import monkey as curious_george
    from gevent.pool import Pool
except ImportError:
    raise RuntimeError('Gevent is required for grequests.')

# Monkey-patch.
curious_george.patch_all(thread=False, select=False)

from requests import Session

__all__ = (
    'map', 'imap',
    'get', 'options', 'head', 'post', 'put', 'patch', 'delete', 'request'
)


class AsyncRequest(object):
    """ Asynchronous request.

    Accept same parameters as ``Session.request`` and some additional:

    :param session: Session which will do request
    :param callback: Callback called on response.
                     Same as passing ``hooks={'response': callback}``
    """
    def __init__(self, method, url, **kwargs):
        #: Request method
        self.method = method
        #: URL to request
        self.url = url
        #: Associated ``Session``
        self.session = kwargs.pop('session', None)
        if self.session is None:
            self.session = Session()
            self._close = True
        else:
            self._close = False  # don't close adapters after each request if the user provided the session

        callback = kwargs.pop('callback', None)
        if callback:
            kwargs['hooks'] = {'response': callback}

        #: The rest arguments for ``Session.request``
        self.kwargs = kwargs
        #: Resulting ``Response``
        self.response = None

    def send(self, **kwargs):
        """
        Prepares request based on parameter passed to constructor and optional ``kwargs```.
        Then sends request and saves response to :attr:`response`

        :returns: ``Response``
        """
        merged_kwargs = {}
        merged_kwargs.update(self.kwargs)
        merged_kwargs.update(kwargs)
        try:
            self.response = self.session.request(self.method,
                                                self.url, **merged_kwargs)
        except Exception as e:
            self.exception = e
            self.traceback = traceback.format_exc()
        finally:
            if self._close:
                # if we provided the session object, make sure we're cleaning up
                # because there's no sense in keeping it open at this point if it wont be reused
                self.session.close()
        return self


def send(r, pool=None, stream=False):
    """Sends the request object using the specified pool. If a pool isn't
    specified this method blocks. Pools are useful because you can specify size
    and can hence limit concurrency."""
    if pool is not None:
        return pool.spawn(r.send, stream=stream)

    return gevent.spawn(r.send, stream=stream)


# Shortcuts for creating AsyncRequest with appropriate HTTP method
get = partial(AsyncRequest, 'GET')
options = partial(AsyncRequest, 'OPTIONS')
head = partial(AsyncRequest, 'HEAD')
post = partial(AsyncRequest, 'POST')
put = partial(AsyncRequest, 'PUT')
patch = partial(AsyncRequest, 'PATCH')
delete = partial(AsyncRequest, 'DELETE')

# synonym
def request(method, url, **kwargs):
    return AsyncRequest(method, url, **kwargs)


def map(requests, stream=False, size=None, exception_handler=None, gtimeout=None):
    """Concurrently converts a list of Requests to Responses.

    :param requests: a collection of Request objects.
    :param stream: If True, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. If None, no throttling occurs.
    :param exception_handler: Callback function, called when exception occured. Params: Request, Exception
    :param gtimeout: Gevent joinall timeout in seconds. (Note: unrelated to requests timeout)
    """

    requests = list(requests)

    pool = Pool(size) if size else None
    jobs = [send(r, pool, stream=stream) for r in requests]
    gevent.joinall(jobs, timeout=gtimeout)

    ret = []

    for request in requests:
        if request.response is not None:
            ret.append(request.response)
        elif exception_handler and hasattr(request, 'exception'):
            ret.append(exception_handler(request, request.exception))
        elif exception_handler and not hasattr(request, 'exception'):
            ret.append(exception_handler(request, None))
        else:
            ret.append(None)

    return ret


def imap(requests, stream=False, size=2, exception_handler=None):
    """Concurrently converts a generator object of Requests to
    a generator of Responses.

    :param requests: a generator of Request objects.
    :param stream: If True, the content will not be downloaded immediately.
    :param size: Specifies the number of requests to make at a time. default is 2
    :param exception_handler: Callback function, called when exception occurred. Params: Request, Exception
    """

    pool = Pool(size)

    def send(r):
        return r.send(stream=stream)

    for request in pool.imap_unordered(send, requests):
        if request.response is not None:
            yield request.response
        elif exception_handler:
            ex_result = exception_handler(request, request.exception)
            if ex_result is not None:
                yield ex_result

    pool.join()
