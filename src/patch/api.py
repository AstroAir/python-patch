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
    """Parse a patch file and return a PatchSet object.

    Reads and parses a unified diff file, returning a PatchSet containing
    all the patches found in the file.

    Args:
        filename (str): Path to the patch file to parse.

    Returns:
        Union[PatchSet, bool]: PatchSet object if parsing succeeds,
            False if parsing fails or file cannot be read.

    Raises:
        FileNotFoundError: If the specified file does not exist.
        PermissionError: If the file cannot be read due to permissions.
        IOError: If there are other file reading errors.

    Example:
        >>> patchset = fromfile('changes.patch')
        >>> if patchset:
        ...     print(f"Loaded {len(patchset)} patches")
        ...     success = patchset.apply(strip=1)
        ... else:
        ...     print("Failed to parse patch file")

    Note:
        The file is opened in binary mode to handle different line endings
        and character encodings properly.
    """
    patchset = PatchSet()
    debug("reading %s" % filename)
    fp = open(filename, "rb")
    res = patchset.parse(fp)
    fp.close()
    if res:
        return patchset
    return False


def fromstring(s: Union[str, bytes]) -> Union[PatchSet, bool]:
    """Parse a patch from a string and return a PatchSet object.

    Parses unified diff content from a string or bytes object,
    returning a PatchSet containing all patches found.

    Args:
        s (Union[str, bytes]): Patch content as string or bytes.
            If a string is provided, it will be encoded as UTF-8.

    Returns:
        Union[PatchSet, bool]: PatchSet object if parsing succeeds,
            False if parsing fails.

    Example:
        >>> patch_content = '''--- a/file.txt
        ... +++ b/file.txt
        ... @@ -1,3 +1,3 @@
        ...  line1
        ... -old line
        ... +new line
        ...  line3'''
        >>> patchset = fromstring(patch_content)
        >>> if patchset:
        ...     print(f"Parsed {len(patchset)} patches")
        ...     for patch in patchset:
        ...         print(f"File: {patch.target.decode()}")

    Note:
        This function is useful for parsing patches received from APIs,
        generated programmatically, or stored in variables.
    """
    # Handle both string and bytes input
    if isinstance(s, str):
        s = s.encode("utf-8")

    ps = PatchSet(StringIO(s))
    if ps.errors == 0:
        return ps
    return False


def fromurl(url: str) -> Union[PatchSet, bool]:
    """Parse a patch from a URL and return a PatchSet object.

    Downloads and parses unified diff content from the specified URL,
    returning a PatchSet containing all patches found.

    Args:
        url (str): URL pointing to a patch file or diff content.
            Supports HTTP, HTTPS, and other protocols supported by urllib.

    Returns:
        Union[PatchSet, bool]: PatchSet object if download and parsing succeed,
            False if parsing fails.

    Raises:
        urllib.error.URLError: If the URL cannot be opened or downloaded.
        urllib.error.HTTPError: If HTTP request fails (404, 403, etc.).
        ValueError: If the URL is malformed.

    Example:
        >>> # Download patch from GitHub
        >>> url = 'https://github.com/user/repo/commit/abc123.patch'
        >>> patchset = fromurl(url)
        >>> if patchset:
        ...     print(f"Downloaded {len(patchset)} patches")
        ...     success = patchset.apply(strip=1)
        ... else:
        ...     print("Failed to parse downloaded patch")

    Note:
        This function performs a network request and may take time to complete.
        Consider using appropriate timeouts and error handling in production code.
    """
    ps = PatchSet(urllib_request.urlopen(url))
    if ps.errors == 0:
        return ps
    return False
