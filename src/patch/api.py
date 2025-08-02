"""
Main API functions for patch parsing.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
from typing import Union

from .compat import StringIO, urllib_request
from .core import PatchSet
from .logging_utils import debug


def fromfile(filename: str) -> Union[PatchSet, bool]:
    """Parse patch file. If successful, returns
    PatchSet() object. Otherwise returns False.
    """
    patchset = PatchSet()
    debug("reading %s" % filename)
    fp = open(filename, "rb")
    res = patchset.parse(fp)
    fp.close()
    if res == True:
        return patchset
    return False


def fromstring(s: Union[str, bytes]) -> Union[PatchSet, bool]:
    """Parse text string and return PatchSet()
    object (or False if parsing fails)
    """
    # Handle both string and bytes input
    if isinstance(s, str):
        s = s.encode('utf-8')

    ps = PatchSet(StringIO(s))
    if ps.errors == 0:
        return ps
    return False


def fromurl(url: str) -> Union[PatchSet, bool]:
    """Parse patch from an URL, return False
    if an error occured. Note that this also
    can throw urlopen() exceptions.
    """
    ps = PatchSet(urllib_request.urlopen(url))
    if ps.errors == 0:
        return ps
    return False
