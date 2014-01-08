#! /usr/bin/env python
# -*- coding: utf-8 -*-

from grequests import get, map, imap
from nose.tools import ok_

########### Constants ############
urls = [
        'http://github.com',
        'http://www.google.com', 
        'http://www.psf.org'
        ]
############# tests ##############
def test_get():
    global urls
    to_fetch = (get(url) for url in urls)
    map(to_fetch)
    for fetched in to_fetch:
        ok_(fetched.ok, True)

def test_imap_with_size():
    global urls
    to_fetch = (get(url) for url in urls)
    imap(to_fetch, size = len(urls) - 1)
    for fetching in to_fetch:
        ok_(fetching.send(), True)
