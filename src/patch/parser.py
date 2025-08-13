"""
Patch parsing functionality.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""

import re
from typing import Union, TYPE_CHECKING, Iterator

from .compat import compat_next
from .constants import PLAIN, GIT, HG, SVN
from .logging_utils import debug, warning, debugmode
from .utils import xisabs, xnormpath, xstrip

if TYPE_CHECKING:
    from .core import Patch, PatchSet


class wrapumerate(object):
    """Enumerate wrapper for stream parsing with boolean end-of-stream status.

    Provides a more convenient interface for parsing streams by using boolean
    return values instead of StopIteration exceptions. Tracks line numbers
    and provides easy access to current line content.

    Attributes:
        is_empty (bool): True if the stream has been exhausted.
        line (Union[bytes, bool]): Current line content, or False if exhausted.
        lineno (Union[int, bool]): Current line number (0-based), or False if exhausted.

    Example:
        >>> from io import BytesIO
        >>> stream = BytesIO(b'line1\\nline2\\nline3\\n')
        >>> wrapper = wrapumerate(stream)
        >>> while wrapper.next():
        ...     print(f"Line {wrapper.lineno}: {wrapper.line}")
        Line 0: b'line1\\n'
        Line 1: b'line2\\n'
        Line 2: b'line3\\n'
    """

    def __init__(self, stream: Iterator[bytes]) -> None:
        """Initialize the wrapper with a byte stream.

        Args:
            stream (Iterator[bytes]): Iterable byte stream to wrap.
        """
        self._stream = enumerate(stream)
        self._exhausted = False
        # after end of stream equal to the num of lines
        self._lineno: Union[int, bool] = False
        # will be reset to False after end of stream
        self._line: Union[bytes, bool] = False

    def next(self) -> bool:
        """Try to read the next line and return True if it is available.

        Returns:
            bool: True if a line was successfully read, False if end of stream.

        Example:
            >>> wrapper = wrapumerate(stream)
            >>> if wrapper.next():
            ...     print(f"Got line: {wrapper.line}")
        """
        if self._exhausted:
            return False

        try:
            self._lineno, self._line = compat_next(self._stream)
        except StopIteration:
            self._exhausted = True
            self._line = False
            return False
        return True

    @property
    def is_empty(self) -> bool:
        """Check if the stream has been exhausted.

        Returns:
            bool: True if no more lines are available.
        """
        return self._exhausted

    @property
    def line(self) -> Union[bytes, bool]:
        """Get the current line content.

        Returns:
            Union[bytes, bool]: Current line as bytes, or False if exhausted.
        """
        return self._line

    @property
    def lineno(self) -> Union[int, bool]:
        """Get the current line number.

        Returns:
            Union[int, bool]: Current line number (0-based), or False if exhausted.
        """
        return self._lineno


def detect_type(p: "Patch") -> str:
    """Detect and return the patch format type for the specified Patch object.

    Analyzes patch headers and filename patterns to determine the source
    control system or diff format that generated the patch.

    Args:
        p (Patch): Patch object to analyze.

    Returns:
        str: Patch type constant (SVN, GIT, HG, or PLAIN).
            - SVN: Subversion patches with "Index:" headers
            - GIT: Git patches with "diff --git" and "index" lines
            - HG: Mercurial patches with "diff -r" or HG changeset markers
            - PLAIN: Standard unified diff format

    Example:
        >>> patch = Patch()
        >>> patch.header = [b'diff --git a/file.txt b/file.txt',
        ...                 b'index abc123..def456 100644']
        >>> patch.source = b'a/file.txt'
        >>> patch.target = b'b/file.txt'
        >>> print(detect_type(patch))  # 'git'

    Note:
        This function must be called before normalize_filenames() as it
        relies on the original a/ and b/ prefixes for detection.
    """

    # check for SVN
    #  - header starts with Index:
    #  - next line is ===... delimiter
    #  - filename is followed by revision number
    # TODO add SVN revision
    if (
        len(p.header) > 1
        and p.header[-2].startswith(b"Index: ")
        and p.header[-1].startswith(b"=" * 67)
    ):
        return SVN

    # common checks for both HG and GIT - need to check for None first
    DVCS = False
    if p.source is not None and p.target is not None:
        DVCS = (p.source.startswith(b"a/") or p.source == b"/dev/null") and (
            p.target.startswith(b"b/") or p.target == b"/dev/null"
        )

    # GIT type check
    #  - header[-2] is like "diff --git a/oldname b/newname"
    #  - header[-1] is like "index <hash>..<hash> <mode>"
    # TODO add git rename diffs and add/remove diffs
    #      add git diff with spaced filename
    # TODO http://www.kernel.org/pub/software/scm/git/docs/git-diff.html

    # Git patch header detection
    idx = -1  # Initialize idx
    if len(p.header) > 1:
        # detect the start of diff header - there might be some comments before
        for idx in reversed(range(len(p.header))):
            if p.header[idx].startswith(b"diff --git"):
                break
        if idx >= 0 and p.header[idx].startswith(b"diff --git a/"):
            # Check if there's an index line (typical for Git)
            if idx + 1 < len(p.header) and re.match(
                b"index \\w+\\.\\.\\w+ \\d+", p.header[idx + 1]
            ):
                if DVCS:
                    return GIT

    # HG check
    #
    #  - for plain HG format header is like "diff -r b2d9961ff1f5 filename"
    #  - for Git-style HG patches it is "diff --git a/oldname b/newname"
    #  - filename starts with a/, b/ or is equal to /dev/null
    #  - exported changesets also contain the header
    #    # HG changeset patch
    #    # User name@example.com
    #    ...
    # TODO add MQ
    # TODO add revision info
    if len(p.header) > 0:
        if DVCS and re.match(b"diff -r \\w+ .*", p.header[-1]):
            return HG
        # Check for HG changeset patch marker or Git-style HG patches
        if DVCS and p.header[-1].startswith(b"diff --git a/"):
            if len(p.header) == 1:  # Git-style HG patch has only one header line
                return HG
            elif p.header[0].startswith(b"# HG changeset patch"):
                return HG

    return PLAIN


def normalize_filenames(patchset: "PatchSet") -> None:
    """Sanitize and normalize filenames in all patches for security and compatibility.

    Performs several important normalizations to ensure patches can be safely
    applied and work across different platforms:

    1. Strip a/ and b/ prefixes from Git and Mercurial style patches
    2. Remove all references to parent directories (../) with warnings
    3. Convert absolute paths to relative paths with warnings
    4. Normalize path separators to forward slashes for cross-platform compatibility

    Args:
        patchset (PatchSet): PatchSet containing patches to normalize.

    Returns:
        None: Modifies the patchset in place.

    Example:
        >>> patchset = PatchSet()
        >>> # Before normalization: source=b'a/path/to/file.txt'
        >>> normalize_filenames(patchset)
        >>> # After normalization: source=b'path/to/file.txt'

    Security Note:
        This function is critical for security as it prevents:
        - Directory traversal attacks via ../ sequences
        - Absolute path exploits that could overwrite system files
        - Platform-specific path issues

    Warning:
        Issues warnings for any suspicious path patterns and increments
        the patchset's warning counter.
    """
    if debugmode:
        debug("normalize filenames")
    for i, p in enumerate(patchset.items):
        if debugmode:
            debug("    patch type = %s" % (p.type or "None"))
            debug("    source = %r" % p.source)
            debug("    target = %r" % p.target)
        if p.type in (HG, GIT):
            # TODO: figure out how to deal with /dev/null entries
            debug("stripping a/ and b/ prefixes")
            if p.source != b"/dev/null" and p.source is not None:
                if not p.source.startswith(b"a/"):
                    warning("invalid source filename")
                    patchset.warnings += 1
                else:
                    p.source = p.source[2:]
            if p.target != b"/dev/null" and p.target is not None:
                if not p.target.startswith(b"b/"):
                    warning("invalid target filename")
                    patchset.warnings += 1
                else:
                    p.target = p.target[2:]

        # Only normalize if not None
        if p.source is not None:
            p.source = xnormpath(p.source)
        if p.target is not None:
            p.target = xnormpath(p.target)

        sep = b"/"  # sep value can be hardcoded, but it looks nice this way

        # references to parent are not allowed
        if p.source is not None and p.source.startswith(b".." + sep):
            warning(
                "error: stripping parent path for source file patch no.%d" % (
                    i + 1)
            )
            patchset.warnings += 1
            while p.source.startswith(b".." + sep):
                p.source = p.source.partition(sep)[2]
        if p.target is not None and p.target.startswith(b".." + sep):
            warning(
                "error: stripping parent path for target file patch no.%d" % (
                    i + 1)
            )
            patchset.warnings += 1
            while p.target.startswith(b".." + sep):
                p.target = p.target.partition(sep)[2]
        # absolute paths are not allowed (except /dev/null)
        source_is_abs = (
            p.source is not None and xisabs(
                p.source) and p.source != b"/dev/null"
        )
        target_is_abs = (
            p.target is not None and xisabs(
                p.target) and p.target != b"/dev/null"
        )

        if source_is_abs or target_is_abs:
            warning("error: absolute paths are not allowed - file no.%d" % (i + 1))
            patchset.warnings += 1
            if source_is_abs and p.source is not None:
                warning("stripping absolute path from source name %r" %
                        p.source)
                p.source = xstrip(p.source)
            if target_is_abs and p.target is not None:
                warning("stripping absolute path from target name %r" %
                        p.target)
                p.target = xstrip(p.target)

        patchset.items[i].source = p.source
        patchset.items[i].target = p.target
