GRequests: Asynchronous Requests
===============================

GRequests allows you to use Requests with Gevent to make asynchronous HTTP
Requests easily.


Usage
-----

Usage is simple::

    import grequests

    urls = [
        'http://www.heroku.com',
        'http://python-tablib.org',
        'http://httpbin.org',
        'http://python-requests.org',
        'http://kennethreitz.com'
    ]

Create a set of unsent Requests::

    >>> rs = (grequests.get(u) for u in urls)

Send them all at the same time::

    >>> grequests.map(rs)
    [<Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>, <Response [200]>]

If you want to add context to a call::

    import grequests

    urls = {
        'http://www.heroku.com': 'heroku',
        'http://python-tablib.org': 'python',
        'http://httpbin.org': 'httpbin',
        'http://www.google.com': 'google'
    }

    rs = (grequests.context(k, context=v) for k,v in urls.iteritems())
    grequests.map(rs)

    [(<Response [200]>, 'google'), (<Response [200]>, 'heroku'), (<Response [200]>, 'python'), (<Response [200]>, 'httpbin')]

Installation
------------

Installation is easy with pip::

    $ pip install grequests
