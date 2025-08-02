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
    """Enumerate wrapper that uses boolean end of stream status instead of
    StopIteration exception, and properties to access line information.
    """

    def __init__(self, stream: Iterator[bytes]) -> None:
        self._stream = enumerate(stream)
        self._exhausted = False
        # after end of stream equal to the num of lines
        self._lineno: Union[int, bool] = False
        # will be reset to False after end of stream
        self._line: Union[bytes, bool] = False

    def next(self) -> bool:
        """Try to read the next line and return True if it is available,
        False if end of stream is reached."""
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
        return self._exhausted

    @property
    def line(self) -> Union[bytes, bool]:
        return self._line

    @property
    def lineno(self) -> Union[int, bool]:
        return self._lineno


def detect_type(p: "Patch") -> str:
    """detect and return type for the specified Patch object
    analyzes header and filenames info

    NOTE: must be run before filenames are normalized
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
    """sanitize filenames, normalizing paths, i.e.:
    1. strip a/ and b/ prefixes from GIT and HG style patches
    2. remove all references to parent directories (with warning)
    3. translate any absolute paths to relative (with warning)

    [x] always use forward slashes to be crossplatform
        (diff/patch were born as a unix utility after all)

    return None
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
                "error: stripping parent path for source file patch no.%d" % (i + 1)
            )
            patchset.warnings += 1
            while p.source.startswith(b".." + sep):
                p.source = p.source.partition(sep)[2]
        if p.target is not None and p.target.startswith(b".." + sep):
            warning(
                "error: stripping parent path for target file patch no.%d" % (i + 1)
            )
            patchset.warnings += 1
            while p.target.startswith(b".." + sep):
                p.target = p.target.partition(sep)[2]
        # absolute paths are not allowed (except /dev/null)
        source_is_abs = (
            p.source is not None and xisabs(p.source) and p.source != b"/dev/null"
        )
        target_is_abs = (
            p.target is not None and xisabs(p.target) and p.target != b"/dev/null"
        )

        if source_is_abs or target_is_abs:
            warning("error: absolute paths are not allowed - file no.%d" % (i + 1))
            patchset.warnings += 1
            if source_is_abs and p.source is not None:
                warning("stripping absolute path from source name %r" % p.source)
                p.source = xstrip(p.source)
            if target_is_abs and p.target is not None:
                warning("stripping absolute path from target name %r" % p.target)
                p.target = xstrip(p.target)

        patchset.items[i].source = p.source
        patchset.items[i].target = p.target
