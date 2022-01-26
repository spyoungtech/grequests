GRequests: Asynchronous Requests
===============================

GRequests allows you to use Requests with Gevent to make asynchronous HTTP
Requests easily.

|version| |pyversions|


**Note**: You should probably use `requests-threads <https://github.com/requests/requests-threads>`_ or `requests-futures <https://github.com/ross/requests-futures>`_ instead.


Installation
------------

Installation is easy with pip::

    $ pip install grequests
    ✨🍰✨


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


The HTTP verb methods in ``grequests`` (``grequests.get``, ``grequests.post``, etc) accept all the same keyword arguments as in the ``requests`` library.

To handle timeouts or any other exception during the connection of
the request, you can add an optional exception handler that will be called with the request and
exception inside the main thread:

.. code-block:: python

    >>> def exception_handler(request, exception):
    ...    print("Request failed")

    >>> reqs = [
    ...    grequests.get('http://httpbin.org/delay/1', timeout=0.001),
    ...    grequests.get('http://fakedomain/'),
    ...    grequests.get('http://httpbin.org/status/500')]
    >>> grequests.map(reqs, exception_handler=exception_handler)
    Request failed
    Request failed
    [None, None, <Response [500]>]

For some speed/performance gains, you may also want to use ``imap`` instead of ``map``. ``imap`` returns a generator of responses. Order of these responses does not map to the order of the requests you send out. The API for ``imap`` is equivalent to the API for ``map``. You can also adjust the ``size`` argument to ``map`` or ``imap`` to increase the gevent pool size.


.. code-block:: python

    for resp in grequests.imap(reqs, size=10):
        print(resp)



NOTE: because ``grequests`` leverages ``gevent`` (which in turn uses monkeypatching for enabling concurrency), you will often need to make sure ``grequests`` is imported before other libraries, especially ``requests``, to avoid problems. See `grequests gevent issues <https://github.com/spyoungtech/grequests/issues?q=is%3Aissue+label%3A%22%3Ahear_no_evil%3A%3Asee_no_evil%3A%3Aspeak_no_evil%3A++gevent%22+>`_ for additional information.


.. code-block:: python

    # GOOD
    import grequests
    import requests
    
    # BAD
    import requests
    import grequests







.. |version| image:: https://img.shields.io/pypi/v/grequests.svg?colorB=blue
    :target: https://pypi.org/project/grequests/

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/grequests.svg?
    :target: https://pypi.org/project/grequests/
    
    
