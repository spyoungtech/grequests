# -*- coding: utf-8 -*-
"""
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


Installation
------------

Installation is easy with pip::

    $ pip install grequests

"""

from setuptools import setup

setup(
    name='grequests',
    version='0.3.0',
    url='https://github.com/kennethreitz/grequests',
    license='BSD',
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    description='Requests + Gevent',
    long_description=__doc__,
    install_requires=[
        'gevent',
        'requests'
    ],
    tests_require = ['nose'],
    test_suite = 'nose.collector',
    py_modules=['grequests'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
