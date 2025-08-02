"""
Utility functions for path handling and other operations.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""
import os
import posixpath
import re


# x...() function are used to work with paths in
# cross-platform manner - all paths use forward
# slashes even on Windows.

def xisabs(filename):
    """Cross-platform version of `os.path.isabs()`
    Returns True if `filename` is absolute on
    Linux, OS X or Windows.
    """
    if filename.startswith(b'/'):     # Linux/Unix
        return True
    elif filename.startswith(b'\\'):  # Windows
        return True
    elif re.match(b'\\w:[\\\\/]', filename):  # Windows
        return True
    return False


def xnormpath(path):
    """Cross-platform version of os.path.normpath"""
    # replace escapes and Windows slashes
    normalized = posixpath.normpath(path).replace(b'\\', b'/')
    # fold the result
    return posixpath.normpath(normalized)


def xstrip(filename):
    """Make relative path out of absolute by stripping
    prefixes used on Linux, OS X and Windows.

    This function is critical for security.
    """
    while xisabs(filename):
        # strip windows drive with all slashes
        if re.match(b'\\w:[\\\\/]', filename):
            filename = re.sub(b'^\\w+:[\\\\/]+', b'', filename)
        # strip all slashes
        elif re.match(b'[\\\\/]', filename):
            filename = re.sub(b'^[\\\\/]+', b'', filename)
    return filename


def pathstrip(path, n):
    """Strip n leading components from the given path"""
    pathlist = [path]
    while os.path.dirname(pathlist[0]) != b'':
        pathlist[0:1] = os.path.split(pathlist[0])

    # If n is greater than or equal to the number of components,
    # return the last component (filename)
    if n >= len(pathlist):
        return pathlist[-1] if pathlist else b''

    return b'/'.join(pathlist[n:])
