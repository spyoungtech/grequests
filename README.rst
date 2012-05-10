GRequests: Asyncronous Requests
===============================

GRequests allows you to use Requests with Gevent to make asyncronous HTTP
Requests easily.


Usage
-----

Usage is simple::

    import grequests

    urls = [
        'http://www.heroku.com',
        'http://tablib.org',
        'http://httpbin.org',
        'http://python-requests.org',
        'http://kennethreitz.com'
    ]

Create a set of unsent Requests::

    >>> rs = (grequests.get(u) for u in urls)

Send them all at the same time::

    >>> grequests.map(rs)
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]


Installation
------------

Installation is easy with pip::

    $ pip install grequests