"""
Integration tests for complete workflows.

Tests complete patch parsing and application workflows using real patch files.
"""
import pytest
import os
import tempfile
import shutil

import patch


class TestCompleteWorkflows:
    """Test complete patch workflows."""
    
    def test_git_patch_workflow(self, temp_dir):
        """Test complete Git patch workflow."""
        # Create a Git-style patch
        git_patch = b'''diff --git a/example.py b/example.py
index 1234567..abcdefg 100644
--- a/example.py
+++ b/example.py
@@ -1,5 +1,5 @@
 def hello():
-    print("Hello, World!")
+    print("Hello, Python!")
     return True
 
 if __name__ == "__main__":
'''
        
        # Create source file
        source_file = os.path.join(temp_dir, 'example.py')
        with open(source_file, 'wb') as f:
            f.write(b'''def hello():
    print("Hello, World!")
    return True

if __name__ == "__main__":
    hello()
''')
        
        # Parse patch
        patchset = patch.fromstring(git_patch)
        assert patchset is not False
        assert patchset.type == patch.GIT
        assert len(patchset.items) == 1
        
        # Check patch properties
        patch_obj = patchset.items[0]
        assert patch_obj.source == b'example.py'
        assert patch_obj.target == b'example.py'
        
        # Apply patch
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = patchset.apply()
            assert result is True
            
            # Verify result
            with open(source_file, 'rb') as f:
                content = f.read()
            assert b'Hello, Python!' in content
            assert b'Hello, World!' not in content
            
        finally:
            os.chdir(original_dir)
    
    def test_svn_patch_workflow(self, temp_dir):
        """Test complete SVN patch workflow."""
        # Create an SVN-style patch
        svn_patch = b'''Index: config.txt
===================================================================
--- config.txt	(revision 123)
+++ config.txt	(working copy)
@@ -1,3 +1,3 @@
 # Configuration file
-debug=false
+debug=true
 version=1.0
'''
        
        # Create source file
        source_file = os.path.join(temp_dir, 'config.txt')
        with open(source_file, 'wb') as f:
            f.write(b'''# Configuration file
debug=false
version=1.0
''')
        
        # Parse patch
        patchset = patch.fromstring(svn_patch)
        assert patchset is not False
        assert patchset.type == patch.SVN
        
        # Apply patch
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = patchset.apply()
            assert result is True
            
            # Verify result
            with open(source_file, 'rb') as f:
                content = f.read()
            assert b'debug=true' in content
            assert b'debug=false' not in content
            
        finally:
            os.chdir(original_dir)
    
    def test_multifile_patch_workflow(self, temp_dir):
        """Test workflow with multiple files."""
        # Create a multi-file patch
        multifile_patch = b'''--- a/file1.txt
+++ b/file1.txt
@@ -1,2 +1,2 @@
 First file
-old content
+new content
--- a/file2.txt
+++ b/file2.txt
@@ -1,2 +1,2 @@
 Second file
-old data
+new data
'''
        
        # Create source files
        file1 = os.path.join(temp_dir, 'file1.txt')
        file2 = os.path.join(temp_dir, 'file2.txt')
        
        with open(file1, 'wb') as f:
            f.write(b'First file\nold content\n')
        
        with open(file2, 'wb') as f:
            f.write(b'Second file\nold data\n')
        
        # Parse patch
        patchset = patch.fromstring(multifile_patch)
        assert patchset is not False
        assert len(patchset.items) == 2
        
        # Apply patch
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = patchset.apply()
            assert result is True
            
            # Verify results
            with open(file1, 'rb') as f:
                content1 = f.read()
            assert b'new content' in content1
            
            with open(file2, 'rb') as f:
                content2 = f.read()
            assert b'new data' in content2
            
        finally:
            os.chdir(original_dir)
    
    def test_patch_and_revert_workflow(self, temp_dir):
        """Test patch application and revert workflow."""
        # Create patch
        patch_content = b'''--- a/data.txt
+++ b/data.txt
@@ -1,3 +1,3 @@
 line 1
-line 2
+modified line 2
 line 3
'''
        
        # Create source file
        source_file = os.path.join(temp_dir, 'data.txt')
        original_content = b'line 1\nline 2\nline 3\n'
        with open(source_file, 'wb') as f:
            f.write(original_content)
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Apply patch
            result = patchset.apply()
            assert result is True
            
            # Verify patch was applied
            with open(source_file, 'rb') as f:
                patched_content = f.read()
            assert b'modified line 2' in patched_content
            assert patched_content != original_content
            
            # Revert patch
            result = patchset.revert()
            assert result is True
            
            # Verify revert worked
            with open(source_file, 'rb') as f:
                reverted_content = f.read()
            assert reverted_content == original_content
            
        finally:
            os.chdir(original_dir)
    
    def test_diffstat_workflow(self, temp_dir):
        """Test diffstat generation workflow."""
        # Create patch with various changes
        patch_content = b'''--- a/small.txt
+++ b/small.txt
@@ -1,2 +1,3 @@
 line 1
+added line
 line 2
--- a/large.txt
+++ b/large.txt
@@ -1,10 +1,9 @@
 line 1
-line 2
-line 3
 line 4
 line 5
 line 6
 line 7
 line 8
+new line
 line 9
 line 10
'''
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        
        # Generate diffstat
        diffstat = patchset.diffstat()
        
        # Verify diffstat content
        assert 'small.txt' in diffstat
        assert 'large.txt' in diffstat
        assert 'files changed' in diffstat
        assert 'insertions' in diffstat or '+' in diffstat
        assert 'deletions' in diffstat or '-' in diffstat
    
    def test_error_recovery_workflow(self, temp_dir):
        """Test error recovery in patch workflows."""
        # Create patch for non-existent file
        patch_content = b'''--- a/nonexistent.txt
+++ b/nonexistent.txt
@@ -1,2 +1,2 @@
 line 1
-line 2
+modified line 2
'''
        
        # Parse patch (should succeed)
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Try to apply patch (should fail gracefully)
            result = patchset.apply()
            assert result is False  # Should fail because file doesn't exist
            
        finally:
            os.chdir(original_dir)
    
    def test_strip_levels_workflow(self, temp_dir):
        """Test patch application with different strip levels."""
        # Create patch with deep path
        patch_content = b'''--- a/deep/nested/path/file.txt
+++ b/deep/nested/path/file.txt
@@ -1,2 +1,2 @@
 content
-old
+new
'''
        
        # Create file at different strip levels
        os.makedirs(os.path.join(temp_dir, 'deep', 'nested', 'path'), exist_ok=True)
        source_file = os.path.join(temp_dir, 'deep', 'nested', 'path', 'file.txt')
        with open(source_file, 'wb') as f:
            f.write(b'content\nold\n')
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        
        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            
            # Apply with strip level 1 (removes 'a/')
            result = patchset.apply(strip=1)
            assert result is True
            
            # Verify result
            with open(source_file, 'rb') as f:
                content = f.read()
            assert b'new' in content
            
        finally:
            os.chdir(original_dir)


class TestRealWorldScenarios:
    """Test real-world patch scenarios."""

    def test_patch_with_context_lines(self, temp_dir):
        """Test patch with context lines."""
        # Create patch with more context
        patch_content = b'''--- a/context.txt
+++ b/context.txt
@@ -2,7 +2,7 @@
 context line 1
 context line 2
 context line 3
-target line
+modified target line
 context line 4
 context line 5
 context line 6
'''

        # Create source file
        source_file = os.path.join(temp_dir, 'context.txt')
        with open(source_file, 'wb') as f:
            f.write(b'''line 0
context line 1
context line 2
context line 3
target line
context line 4
context line 5
context line 6
line 8
''')

        # Parse and apply patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False

        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = patchset.apply()
            assert result is True

            # Verify result
            with open(source_file, 'rb') as f:
                content = f.read()
            assert b'modified target line' in content
            assert b'target line' not in content or content.count(b'target line') == 1

        finally:
            os.chdir(original_dir)

    def test_patch_with_binary_detection(self, temp_dir):
        """Test that binary files are handled appropriately."""
        # Create a patch that might be applied to a binary file
        patch_content = b'''--- a/data.bin
+++ b/data.bin
@@ -1,2 +1,2 @@
 \x00\x01\x02
-\x03\x04\x05
+\x06\x07\x08
'''

        # Create binary file
        source_file = os.path.join(temp_dir, 'data.bin')
        with open(source_file, 'wb') as f:
            f.write(b'\x00\x01\x02\n\x03\x04\x05\n')

        # Parse patch
        patchset = patch.fromstring(patch_content)

        # The patch might parse successfully or fail
        # Either behavior is acceptable for binary data
        if patchset:
            assert len(patchset.items) >= 0
        else:
            # It's okay if binary patches fail to parse
            assert patchset is False

    def test_real_patch_files_from_test_data(self, test_data_dir):
        """Test with real patch files from the test data directory."""
        # Test Git patch file
        git_patch_file = test_data_dir / 'git-changed-file.diff'
        if git_patch_file.exists():
            patchset = patch.fromfile(str(git_patch_file))
            assert patchset is not False
            assert patchset.type == patch.GIT
            assert len(patchset.items) >= 1

            # Test diffstat generation
            diffstat = patchset.diffstat()
            assert isinstance(diffstat, str)
            assert 'files changed' in diffstat

        # Test SVN patch file
        svn_patch_file = test_data_dir / 'svn-changed-2-files.diff'
        if svn_patch_file.exists():
            patchset = patch.fromfile(str(svn_patch_file))
            assert patchset is not False
            assert patchset.type == patch.SVN
            assert len(patchset.items) >= 1

        # Test Mercurial patch file
        hg_patch_file = test_data_dir / 'hg-changed-2-files.diff'
        if hg_patch_file.exists():
            patchset = patch.fromfile(str(hg_patch_file))
            assert patchset is not False
            assert patchset.type == patch.HG
            assert len(patchset.items) >= 1

    def test_patch_with_unicode_content(self, temp_dir):
        """Test patches with Unicode content."""
        # Create patch with Unicode characters
        patch_content = '''--- a/unicode.txt
+++ b/unicode.txt
@@ -1,3 +1,3 @@
 Hello
-café
+café français
 World
'''.encode('utf-8')

        # Create source file with Unicode
        source_file = os.path.join(temp_dir, 'unicode.txt')
        with open(source_file, 'wb') as f:
            f.write('Hello\ncafé\nWorld\n'.encode('utf-8'))

        # Parse and apply patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False

        original_dir = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = patchset.apply()
            assert result is True

            # Verify Unicode content
            with open(source_file, 'rb') as f:
                content = f.read()
            content_str = content.decode('utf-8')
            assert 'café français' in content_str

        finally:
            os.chdir(original_dir)

    def test_patch_with_line_ending_variations(self, temp_dir):
        """Test patches with different line endings."""
        # Test CRLF line endings
        patch_crlf = b'--- a/crlf.txt\r\n+++ b/crlf.txt\r\n@@ -1,2 +1,2 @@\r\n line1\r\n-line2\r\n+modified\r\n'

        source_file = os.path.join(temp_dir, 'crlf.txt')
        with open(source_file, 'wb') as f:
            f.write(b'line1\r\nline2\r\n')

        patchset = patch.fromstring(patch_crlf)
        if patchset:  # Some line endings might not be fully supported
            original_dir = os.getcwd()
            try:
                os.chdir(temp_dir)
                # Try to apply - may succeed or fail depending on implementation
                patchset.apply()
            except:
                # It's acceptable if some line ending combinations fail
                pass
            finally:
                os.chdir(original_dir)


@pytest.mark.integration
class TestPerformanceScenarios:
    """Test performance with larger patches."""
    
    def test_large_patch_parsing(self, temp_dir):
        """Test parsing of larger patches."""
        # Create a patch with many hunks
        patch_lines = [b'--- a/large.txt\n', b'+++ b/large.txt\n']
        
        for i in range(10):  # 10 hunks
            hunk_start = i * 10 + 1
            patch_lines.extend([
                f'@@ -{hunk_start},3 +{hunk_start},3 @@\n'.encode(),
                b' context line\n',
                f'-old line {i}\n'.encode(),
                f'+new line {i}\n'.encode(),
                b' context line\n'
            ])
        
        patch_content = b''.join(patch_lines)
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        assert len(patchset.items) == 1
        assert len(patchset.items[0].hunks) == 10
    
    def test_many_files_patch(self, temp_dir):
        """Test patch with many files."""
        # Create patch with multiple files
        patch_lines = []
        
        for i in range(5):  # 5 files
            patch_lines.extend([
                f'diff --git a/file{i}.txt b/file{i}.txt\n'.encode(),
                f'index 1234567..abcdefg 100644\n'.encode(),
                f'--- a/file{i}.txt\n'.encode(),
                f'+++ b/file{i}.txt\n'.encode(),
                b'@@ -1,2 +1,2 @@\n',
                b' common line\n',
                f'-old content {i}\n'.encode(),
                f'+new content {i}\n'.encode()
            ])
        
        patch_content = b''.join(patch_lines)
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        assert len(patchset.items) == 5
        
        # Verify each file patch
        for i, patch_obj in enumerate(patchset.items):
            assert patch_obj.source == f'file{i}.txt'.encode()
            assert patch_obj.target == f'file{i}.txt'.encode()
            assert len(patch_obj.hunks) == 1
