"""
Patch utility to apply unified diffs

Brute-force line-by-line non-recursive parsing 

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license

This package provides a modern, well-organized structure while maintaining
100% backward compatibility with the original patch.py module.
"""
from __future__ import print_function

# Import all public API to maintain backward compatibility
from .api import fromfile, fromstring, fromurl
from .cli import main
from .constants import (
    __author__, __version__, __license__, __url__,
    DIFF, PLAIN, GIT, HG, MERCURIAL, SVN, SUBVERSION, MIXED
)
from .core import Hunk, Patch, PatchSet
from .logging_utils import setdebug, debug, info, warning, debugmode
from .utils import xisabs, xnormpath, xstrip, pathstrip

# For backward compatibility, expose all the original module-level functions and classes
__all__ = [
    # Main API functions
    'fromfile', 'fromstring', 'fromurl', 'main',
    
    # Core classes
    'Hunk', 'Patch', 'PatchSet',
    
    # Constants
    'DIFF', 'PLAIN', 'GIT', 'HG', 'MERCURIAL', 'SVN', 'SUBVERSION', 'MIXED',
    
    # Utility functions
    'xisabs', 'xnormpath', 'xstrip', 'pathstrip',
    
    # Logging
    'setdebug', 'debug', 'info', 'warning', 'debugmode',
    
    # Metadata
    '__author__', '__version__', '__license__', '__url__'
]
