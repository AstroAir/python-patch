#!/usr/bin/env python
"""
Backward compatibility wrapper for the refactored patch module.

This file maintains 100% backward compatibility with the original patch.py
while using the new modular structure under src/patch/.

Copyright (c) 2008-2016 anatoly techtonik
Available under the terms of MIT license
"""

# Add src to path so we can import the new structure
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import everything from the new patch package to maintain compatibility
from patch import *

# Ensure the main function can be called when this file is executed directly
if __name__ == "__main__":
    main()
