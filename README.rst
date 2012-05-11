ERequests: Asyncronous Requests
===============================

ERequests allows you to use Requests with Eventlet to make asyncronous HTTP
Requests easily.

ERequests is a port to Eventlet of Kenneth Reitz's grequests (https://github.com/kennethreitz/grequests)

Usage
-----

Usage is simple::

    import erequests

    urls = [
        'http://www.heroku.com',
        'http://tablib.org',
        'http://httpbin.org',
        'http://python-requests.org',
        'http://kennethreitz.com'
    ]

Create a set of unsent Requests::

    >>> rs = (erequests.get(u) for u in urls)

Send them all at the same time::

    >>> erequests.map(rs)
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]


Installation
------------

Installation is easy with pip::

    $ pip install erequests

