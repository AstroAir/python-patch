"""
Constants for patch types and compatibility.

Copyright (c) 2008-2016 anatoly techtonik
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
__author__ = "anatoly techtonik <techtonik@gmail.com>"
__version__ = "1.16"
__license__ = "MIT"
__url__ = "https://github.com/techtonik/python-patch"
