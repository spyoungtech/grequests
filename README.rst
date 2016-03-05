GRequests: Asynchronous Requests
===============================

GRequests allows you to use Requests with Gevent to make asynchronous HTTP
Requests easily.


Usage
-----

Usage is simple:

.. code-block:: python

    import grequests

    urls = [
        'http://www.heroku.com',
        'http://python-tablib.org',
        'http://httpbin.org',
        'http://python-requests.org',
        'http://fakedomain/',
        'http://kennethreitz.com'
    ]

Create a set of unsent Requests:

.. code-block:: python

    >>> rs = (grequests.get(u) for u in urls)

Send them all at the same time:

.. code-block:: python

    >>> grequests.map(rs)
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, None, <Response [200]>]

Optionally, in the event of a timeout or any other exception during the connection of
the request, you can add an exception handler that will be called with the request and
exception inside the main thread:

.. code-block:: python

    >>> def exception_handler(request, exception):
    ...    print "Request failed"

    >>> reqs = [
    ...    grequests.get('http://httpbin.org/delay/1', timeout=0.001),
    ...    grequests.get('http://fakedomain/'),
    ...    grequests.get('http://httpbin.org/status/500')]
    >>> grequests.map(reqs, exception_handler=exception_handler)
    Request failed
    Request failed
    [None, None, <Response [500]>]


You can also specify the exception_handler on per request basis by passing the
keyword argument *exception_handler* to grequests.get(), grequests.post(), etc.
The exception_handler will be called asynchronously, in contrast to passing
*exception_handler* to grequests.map(), where the exception_handler will be called
 after all the requests are joined.

.. code-block:: python

    >>> def exception_handler(request, exception):
    ...    print request.url, "| request failed"

    >>> reqs = [
    ...    grequests.get('http://httpbin.org/delay/1', timeout=0.001, exception_handler=exception_handler),
    ...    grequests.get('http://fakedomain/', exception_handler=exception_handler),
    ...    grequests.get('http://httpbin.org/status/500', exception_handler=exception_handler)]
    >>> grequests.map(reqs)
    http://fakedomain/ | request failed
    http://httpbin.org/delay/1 | request failed
    [None, None, <Response [500]>]

Installation
------------

Installation is easy with pip::

    $ pip install grequests
