"""
Compatibility utilities for Python 2/3 support.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
from __future__ import print_function

import sys

# cStringIO doesn't support unicode in 2.5
try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO  # python 3

try:
    import urllib2 as urllib_request
except ImportError:
    import urllib.request as urllib_request

PY3K = sys.version_info >= (3, 0)

# PEP 3114
if not PY3K:
    compat_next = lambda gen: gen.next()
else:
    compat_next = lambda gen: gen.__next__()


def tostr(b):
    """Python 3 bytes encoder. Used to print filename in
    diffstat output. Assumes that filenames are in utf-8.
    """
    if not PY3K:
        return b

    # [ ] figure out how to print non-utf-8 filenames without
    #     information loss
    return b.decode('utf-8')
