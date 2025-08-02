"""
Constants for patch types and compatibility.

Copyright (c) 2025 Max Qian <astro_air@126.com>
Available under the terms of MIT license
"""

# Patch/PatchSet type constants
DIFF = PLAIN = "plain"
GIT = "git"
HG = MERCURIAL = "mercurial"
SVN = SUBVERSION = "svn"
# mixed type is only actual when PatchSet contains
# Patches of different type
MIXED = "mixed"

# Module metadata
__author__ = "Max Qian <astro_air@126.com>"
__version__ = "1.0.0"
__license__ = "MIT"
__url__ = "https://github.com/AstroAir/python-patch"
