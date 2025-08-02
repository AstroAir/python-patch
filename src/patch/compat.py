"""
Compatibility utilities for Python 2/3 support.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""

from __future__ import print_function

import sys
from typing import Union, TypeVar, Iterator

# cStringIO doesn't support unicode in 2.5
try:
    from StringIO import StringIO  # type: ignore[import-not-found]
except ImportError:
    # python 3: StringIO is a binary buffer equivalent for legacy use
    from io import BytesIO as StringIO  # type: ignore[assignment]

try:
    import urllib2 as urllib_request  # type: ignore[import-not-found]
except ImportError:
    import urllib.request as urllib_request

PY3K = sys.version_info >= (3, 0)

# Type variable for generic iterator
T = TypeVar("T")

# PEP 3114
if not PY3K:

    def compat_next(gen: Iterator[T]) -> T:
        return gen.next()  # type: ignore[attr-defined,no-any-return]

else:

    def compat_next(gen: Iterator[T]) -> T:
        return gen.__next__()


# Public API of this module
__all__ = [
    "StringIO",
    "urllib_request",
    "PY3K",
    "compat_next",
    "tostr",
]

ByteLike = Union[bytes, bytearray, memoryview]
StrOrByteLike = Union[str, ByteLike]


def _decode_utf8(b: bytes) -> str:
    # Centralized decode to keep mypy/pyright happy
    return b.decode("utf-8", errors="strict")


def tostr(b: StrOrByteLike) -> str:
    """Python 3 bytes encoder. Used to print filename in
    diffstat output. Assumes that filenames are in utf-8.
    Always returns str.
    """
    if not PY3K:
        # In Python 2, tostr historically returned the input for printing.
        # For type checkers in py3 context, this function is only used in py3.
        # type: ignore[return-value]
        return b if isinstance(b, str) else _decode_utf8(bytes(b))

    # [ ] figure out how to print non-utf-8 filenames without information loss
    if isinstance(b, str):
        return b
    if isinstance(b, (bytes, bytearray)):
        return _decode_utf8(bytes(b))
    # memoryview or other buffer-like object
    return _decode_utf8(bytes(b))
