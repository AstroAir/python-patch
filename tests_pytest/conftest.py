"""
Pytest configuration and fixtures for python-patch tests.

This file provides common fixtures and configuration for all test modules.
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add src to path so we can import the patch module
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import patch


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_patch_content():
    """Sample unified diff content for testing."""
    return b'''diff --git a/test.txt b/test.txt
index 1234567..abcdefg 100644
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''


@pytest.fixture
def sample_git_patch():
    """Sample Git patch content."""
    return b'''diff --git a/test.txt b/test.txt
index 1234567..abcdefg 100644
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''


@pytest.fixture
def sample_svn_patch():
    """Sample SVN patch content."""
    return b'''Index: test.txt
===================================================================
--- test.txt	(revision 123)
+++ test.txt	(working copy)
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''


@pytest.fixture
def sample_hg_patch():
    """Sample Mercurial patch content."""
    return b'''diff -r 1234567890ab test.txt
--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''


@pytest.fixture
def sample_file_content():
    """Sample file content for patching."""
    return b'''line1
line2
line3
'''


@pytest.fixture
def expected_patched_content():
    """Expected content after applying patch."""
    return b'''line1
line2_modified
line3
'''


@pytest.fixture
def test_files_dir():
    """Path to the existing test files directory."""
    return Path(__file__).parent.parent / 'tests'


@pytest.fixture
def test_data_dir():
    """Path to the test data directory."""
    return Path(__file__).parent.parent / 'tests' / 'data'


@pytest.fixture
def patch_module():
    """The patch module for testing."""
    return patch


@pytest.fixture
def invalid_patch_content():
    """Invalid patch content for error testing."""
    return b'''This is not a valid patch file
It contains no patch headers
And should cause parsing to fail
'''


@pytest.fixture
def multifile_patch():
    """Multi-file patch content."""
    return b'''diff --git a/file1.txt b/file1.txt
index 1111111..2222222 100644
--- a/file1.txt
+++ b/file1.txt
@@ -1,2 +1,2 @@
 line1
-old_line
+new_line
diff --git a/file2.txt b/file2.txt
index 3333333..4444444 100644
--- a/file2.txt
+++ b/file2.txt
@@ -1,2 +1,2 @@
 content1
-old_content
+new_content
'''


@pytest.fixture
def empty_file_patch():
    """Patch for an empty file."""
    return b'''--- /dev/null
+++ b/newfile.txt
@@ -0,0 +1,2 @@
+first line
+second line
'''


@pytest.fixture
def delete_file_patch():
    """Patch that deletes a file."""
    return b'''--- a/deleteme.txt
+++ /dev/null
@@ -1,2 +0,0 @@
-line to delete
-another line to delete
'''


# Test data for cross-platform path testing
@pytest.fixture
def cross_platform_paths():
    """Cross-platform path test data."""
    return {
        'absolute_unix': [b'/', b'/path', b'/path/to/file'],
        'absolute_windows': [b'c:\\', b'c:/', b'c:\\path', b'c:/path'],
        'relative': [b'path', b'path/to/file', b'path\\to\\file'],
        'mixed': [b'../something/..\\..\\file.to.patch']
    }


@pytest.fixture
def patch_types():
    """Patch type constants for testing."""
    return {
        'PLAIN': patch.PLAIN,
        'GIT': patch.GIT,
        'HG': patch.HG,
        'SVN': patch.SVN,
        'MIXED': patch.MIXED
    }


# Configure pytest
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


# Custom assertion helpers
class PatchAssertions:
    """Custom assertion helpers for patch testing."""
    
    @staticmethod
    def assert_patch_equal(patch1, patch2):
        """Assert that two patches are equal."""
        assert len(patch1.items) == len(patch2.items)
        for p1, p2 in zip(patch1.items, patch2.items):
            assert p1.source == p2.source
            assert p1.target == p2.target
            assert len(p1.hunks) == len(p2.hunks)
            for h1, h2 in zip(p1.hunks, p2.hunks):
                assert h1.startsrc == h2.startsrc
                assert h1.starttgt == h2.starttgt
                assert h1.linessrc == h2.linessrc
                assert h1.linestgt == h2.linestgt
                assert h1.text == h2.text
    
    @staticmethod
    def assert_file_content_equal(file1, file2):
        """Assert that two files have equal content."""
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            assert f1.read() == f2.read()


@pytest.fixture
def patch_assertions():
    """Provide custom patch assertion helpers."""
    return PatchAssertions()
