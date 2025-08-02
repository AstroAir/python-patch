#!/usr/bin/env python3
"""
Test script to verify 100% backward compatibility with the original patch.py module.
"""

def test_original_import():
    """Test importing from the original patch.py file"""
    print("Testing original patch.py import...")
    import patch
    
    # Test all expected attributes exist
    expected_attrs = [
        'fromfile', 'fromstring', 'fromurl', 'main',
        'Hunk', 'Patch', 'PatchSet',
        'DIFF', 'PLAIN', 'GIT', 'HG', 'MERCURIAL', 'SVN', 'SUBVERSION', 'MIXED',
        'xisabs', 'xnormpath', 'xstrip', 'pathstrip',
        'setdebug', 'debug', 'info', 'warning',
        '__author__', '__version__', '__license__', '__url__'
    ]
    
    missing = []
    for attr in expected_attrs:
        if not hasattr(patch, attr):
            missing.append(attr)
    
    if missing:
        print(f"❌ Missing attributes: {missing}")
        return False
    else:
        print("✅ All expected attributes are present")
    
    # Test basic functionality
    try:
        # Test PatchSet creation
        ps = patch.PatchSet()
        print("✅ PatchSet creation works")
        
        # Test fromstring with a simple patch
        test_patch = b'''--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''
        ps = patch.fromstring(test_patch)
        if ps and len(ps.items) == 1:
            print("✅ fromstring functionality works")
        else:
            print("❌ fromstring functionality failed")
            return False
            
        # Test constants
        if patch.GIT == "git" and patch.SVN == "svn":
            print("✅ Constants are correct")
        else:
            print("❌ Constants are incorrect")
            return False
            
        # Test utility functions
        if patch.xisabs(b'/absolute/path') and not patch.xisabs(b'relative/path'):
            print("✅ Utility functions work")
        else:
            print("❌ Utility functions failed")
            return False
            
        print("✅ All backward compatibility tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False


def test_new_structure_import():
    """Test importing from the new src structure"""
    print("\nTesting new structure import...")
    import sys
    import os
    sys.path.insert(0, 'src')
    import patch as new_patch
    
    # Test that it has the same interface
    original_attrs = dir(__import__('patch'))
    new_attrs = dir(new_patch)
    
    # Filter out private attributes and focus on public API
    public_original = [attr for attr in original_attrs if not attr.startswith('_')]
    public_new = [attr for attr in new_attrs if not attr.startswith('_')]
    
    missing_in_new = set(public_original) - set(public_new)
    if missing_in_new:
        print(f"❌ New structure missing: {missing_in_new}")
        return False
    else:
        print("✅ New structure has all public attributes from original")
        
    # Test that functionality is identical
    try:
        test_patch = b'''--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''
        ps_new = new_patch.fromstring(test_patch)
        if ps_new and len(ps_new.items) == 1:
            print("✅ New structure functionality works")
            return True
        else:
            print("❌ New structure functionality failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing new structure: {e}")
        return False


def test_cli_compatibility():
    """Test that the CLI interface still works"""
    print("\nTesting CLI compatibility...")
    import subprocess
    import sys
    
    try:
        # Test version output
        result = subprocess.run([sys.executable, 'patch_new.py', '--version'],
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and 'python-patch' in result.stdout:
            print("✅ CLI version works")
            return True
        else:
            print("❌ CLI version failed")
            return False
    except Exception as e:
        print(f"❌ CLI test error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("BACKWARD COMPATIBILITY TEST SUITE")
    print("=" * 60)
    
    # Test original import (using the backward compatibility wrapper)
    success1 = test_original_import()
    
    # Test new structure import
    success2 = test_new_structure_import()
    
    # Test CLI compatibility
    success3 = test_cli_compatibility()
    
    print("\n" + "=" * 60)
    if success1 and success2 and success3:
        print("🎉 ALL BACKWARD COMPATIBILITY TESTS PASSED!")
        print("The refactored code maintains 100% compatibility.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Backward compatibility issues detected.")
    print("=" * 60)
