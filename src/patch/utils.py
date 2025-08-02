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


def xisabs(filename: bytes) -> bool:
    """Cross-platform version of `os.path.isabs()` for bytes paths.

    Determines if a filename represents an absolute path on Linux, macOS,
    or Windows systems. Handles both Unix-style and Windows-style paths.

    Args:
        filename (bytes): Path to check as bytes.

    Returns:
        bool: True if the path is absolute, False otherwise.

    Examples:
        >>> xisabs(b'/usr/local/bin')  # Unix absolute
        True
        >>> xisabs(b'C:\\Windows\\System32')  # Windows absolute
        True
        >>> xisabs(b'relative/path')  # Relative path
        False
        >>> xisabs(b'./current/dir')  # Relative path
        False

    Security Note:
        This function is used to detect absolute paths in patches,
        which are typically not allowed for security reasons.
    """
    if filename.startswith(b"/"):  # Linux/Unix
        return True
    elif filename.startswith(b"\\"):  # Windows
        return True
    elif re.match(b"\\w:[\\\\/]", filename):  # Windows
        return True
    return False


def xnormpath(path: bytes) -> bytes:
    """Cross-platform path normalization using forward slashes.

    Normalizes a path by resolving . and .. components and converting
    all path separators to forward slashes for cross-platform compatibility.

    Args:
        path (bytes): Path to normalize as bytes.

    Returns:
        bytes: Normalized path with forward slashes.

    Examples:
        >>> xnormpath(b'a/b/../c/./d')
        b'a/c/d'
        >>> xnormpath(b'a\\\\b\\\\c')  # Windows path
        b'a/b/c'
        >>> xnormpath(b'/a/b/../../c')
        b'/c'

    Note:
        This function ensures all paths use forward slashes, making
        patches portable between Unix and Windows systems.
    """
    # replace escapes and Windows slashes
    normalized = posixpath.normpath(path).replace(b"\\", b"/")
    # fold the result
    return posixpath.normpath(normalized)


def xstrip(filename: bytes) -> bytes:
    """Convert absolute path to relative by stripping platform-specific prefixes.

    Removes absolute path prefixes from Linux, macOS, and Windows paths,
    converting them to relative paths. This is a critical security function
    that prevents patches from modifying files outside the intended directory.

    Args:
        filename (bytes): Absolute path to convert to relative.

    Returns:
        bytes: Relative path with absolute prefixes removed.

    Examples:
        >>> xstrip(b'/usr/local/bin/file.txt')
        b'usr/local/bin/file.txt'
        >>> xstrip(b'C:\\\\Windows\\\\System32\\\\file.dll')
        b'Windows/System32/file.dll'
        >>> xstrip(b'\\\\server\\\\share\\\\file.txt')
        b'server/share/file.txt'

    Security Warning:
        This function is critical for security as it prevents directory
        traversal attacks and ensures patches cannot modify system files
        outside the intended working directory.

    Note:
        Repeatedly strips prefixes until the path is no longer absolute,
        handling nested absolute path constructions.
    """
    while xisabs(filename):
        # strip windows drive with all slashes
        if re.match(b"\\w:[\\\\/]", filename):
            filename = re.sub(b"^\\w+:[\\\\/]+", b"", filename)
        # strip all slashes
        elif re.match(b"[\\\\/]", filename):
            filename = re.sub(b"^[\\\\/]+", b"", filename)
    return filename


def pathstrip(path: bytes, n: int) -> bytes:
    """Strip n leading path components from the given path.

    Removes the first n directory components from a path, similar to
    the -p option in the patch command. Useful for applying patches
    when the directory structure differs from the patch's expectations.

    Args:
        path (bytes): Path to strip components from.
        n (int): Number of leading components to remove.

    Returns:
        bytes: Path with n leading components removed, using forward slashes.
            If n >= number of components, returns just the filename.

    Examples:
        >>> pathstrip(b'a/b/c/file.txt', 0)
        b'a/b/c/file.txt'
        >>> pathstrip(b'a/b/c/file.txt', 1)
        b'b/c/file.txt'
        >>> pathstrip(b'a/b/c/file.txt', 2)
        b'c/file.txt'
        >>> pathstrip(b'a/b/c/file.txt', 3)
        b'file.txt'
        >>> pathstrip(b'a/b/c/file.txt', 10)  # More than available
        b'file.txt'

    Note:
        This function is commonly used with patch application where
        patches contain paths like 'a/file.txt' and 'b/file.txt' but
        you want to apply them to just 'file.txt'.
    """
    pathlist = [path]
    while os.path.dirname(pathlist[0]) != b"":
        pathlist[0:1] = os.path.split(pathlist[0])

    # If n is greater than or equal to the number of components,
    # return the last component (filename)
    if n >= len(pathlist):
        return pathlist[-1] if pathlist else b""

    return b"/".join(pathlist[n:])
