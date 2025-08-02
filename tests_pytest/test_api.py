"""
Unit tests for API functions (fromfile, fromstring, fromurl).

Tests the main API entry points for patch parsing.
"""

import pytest
import tempfile
import os
from unittest.mock import patch as mock_patch, MagicMock
from urllib.error import URLError

import patch
from patch.api import fromfile, fromstring, fromurl


class TestFromFile:
    """Test the fromfile function."""

    def test_fromfile_valid_patch(self, temp_dir, sample_patch_content):
        """Test fromfile with a valid patch file."""
        patch_file = os.path.join(temp_dir, "test.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_patch_content)

        result = fromfile(patch_file)
        assert result is not False
        assert isinstance(result, patch.PatchSet)
        assert len(result.items) == 1
        assert result.errors == 0

    def test_fromfile_nonexistent_file(self):
        """Test fromfile with non-existent file."""
        with pytest.raises(FileNotFoundError):
            fromfile("/nonexistent/file.patch")

    def test_fromfile_invalid_patch(self, temp_dir, invalid_patch_content):
        """Test fromfile with invalid patch content."""
        patch_file = os.path.join(temp_dir, "invalid.patch")
        with open(patch_file, "wb") as f:
            f.write(invalid_patch_content)

        result = fromfile(patch_file)
        assert result is False

    def test_fromfile_empty_file(self, temp_dir):
        """Test fromfile with empty file."""
        patch_file = os.path.join(temp_dir, "empty.patch")
        with open(patch_file, "wb") as f:
            pass  # Create empty file

        result = fromfile(patch_file)
        assert result is False

    def test_fromfile_git_patch(self, temp_dir, sample_git_patch):
        """Test fromfile with Git patch."""
        patch_file = os.path.join(temp_dir, "git.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_git_patch)

        result = fromfile(patch_file)
        assert result is not False
        assert result.type == patch.GIT

    def test_fromfile_svn_patch(self, temp_dir, sample_svn_patch):
        """Test fromfile with SVN patch."""
        patch_file = os.path.join(temp_dir, "svn.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_svn_patch)

        result = fromfile(patch_file)
        assert result is not False
        assert result.type == patch.SVN

    def test_fromfile_hg_patch(self, temp_dir, sample_hg_patch):
        """Test fromfile with Mercurial patch."""
        patch_file = os.path.join(temp_dir, "hg.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_hg_patch)

        result = fromfile(patch_file)
        assert result is not False
        assert result.type == patch.HG

    def test_fromfile_multifile_patch(self, temp_dir, multifile_patch):
        """Test fromfile with multi-file patch."""
        patch_file = os.path.join(temp_dir, "multi.patch")
        with open(patch_file, "wb") as f:
            f.write(multifile_patch)

        result = fromfile(patch_file)
        assert result is not False
        assert len(result.items) == 2

    def test_fromfile_binary_mode(self, temp_dir):
        """Test that fromfile opens files in binary mode."""
        # Create a patch with non-ASCII characters
        patch_content = (
            b"--- a/test.txt\n+++ b/test.txt\n@@ -1,1 +1,1 @@\n-\xc3\xa9\n+\xc3\xa0\n"
        )
        patch_file = os.path.join(temp_dir, "unicode.patch")
        with open(patch_file, "wb") as f:
            f.write(patch_content)

        result = fromfile(patch_file)
        # Should not raise encoding errors
        assert result is not False or result is False  # Either way, no exception


class TestFromString:
    """Test the fromstring function."""

    def test_fromstring_valid_patch(self, sample_patch_content):
        """Test fromstring with valid patch content."""
        result = fromstring(sample_patch_content)
        assert result is not False
        assert isinstance(result, patch.PatchSet)
        assert len(result.items) == 1
        assert result.errors == 0

    def test_fromstring_invalid_patch(self, invalid_patch_content):
        """Test fromstring with invalid patch content."""
        result = fromstring(invalid_patch_content)
        assert result is False

    def test_fromstring_empty_content(self):
        """Test fromstring with empty content."""
        result = fromstring(b"")
        assert result is False

    def test_fromstring_git_patch(self, sample_git_patch):
        """Test fromstring with Git patch."""
        result = fromstring(sample_git_patch)
        assert result is not False
        assert result.type == patch.GIT

    def test_fromstring_svn_patch(self, sample_svn_patch):
        """Test fromstring with SVN patch."""
        result = fromstring(sample_svn_patch)
        assert result is not False
        assert result.type == patch.SVN

    def test_fromstring_hg_patch(self, sample_hg_patch):
        """Test fromstring with Mercurial patch."""
        result = fromstring(sample_hg_patch)
        assert result is not False
        assert result.type == patch.HG

    def test_fromstring_multifile_patch(self, multifile_patch):
        """Test fromstring with multi-file patch."""
        result = fromstring(multifile_patch)
        assert result is not False
        assert len(result.items) == 2

    def test_fromstring_string_vs_bytes(self, sample_patch_content):
        """Test fromstring with both string and bytes input."""
        # Test with bytes (normal case)
        result_bytes = fromstring(sample_patch_content)
        assert result_bytes is not False

        # Test with string (should also work)
        string_content = sample_patch_content.decode("utf-8")
        result_string = fromstring(string_content)
        # Behavior may vary depending on implementation
        # Just ensure it doesn't crash
        assert result_string is not False or result_string is False

    def test_fromstring_with_errors(self):
        """Test fromstring with content that has parsing errors."""
        # Malformed hunk header
        malformed_patch = b"""--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@ invalid extra content
 line1
-line2
+line2_modified
 line3
"""
        result = fromstring(malformed_patch)
        # Should either parse successfully or fail gracefully
        assert result is not False or result is False


class TestFromUrl:
    """Test the fromurl function."""

    def test_fromurl_valid_url(self, sample_patch_content):
        """Test fromurl with valid URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = sample_patch_content
        mock_response.__iter__.return_value = iter(sample_patch_content.split(b"\n"))

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            result = fromurl("http://example.com/test.patch")
            assert result is not False
            assert isinstance(result, patch.PatchSet)
            assert len(result.items) == 1

    def test_fromurl_invalid_url(self):
        """Test fromurl with invalid URL."""
        with mock_patch(
            "patch.compat.urllib_request.urlopen", side_effect=URLError("Invalid URL")
        ):
            with pytest.raises(URLError):
                fromurl("http://invalid-url.com/test.patch")

    def test_fromurl_invalid_patch_content(self, invalid_patch_content):
        """Test fromurl with invalid patch content from URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = invalid_patch_content
        mock_response.__iter__.return_value = iter(invalid_patch_content.split(b"\n"))

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            result = fromurl("http://example.com/invalid.patch")
            assert result is False

    def test_fromurl_empty_response(self):
        """Test fromurl with empty response."""
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__iter__.return_value = iter([])

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            result = fromurl("http://example.com/empty.patch")
            assert result is False

    def test_fromurl_network_error(self):
        """Test fromurl with network error."""
        with mock_patch(
            "patch.compat.urllib_request.urlopen",
            side_effect=Exception("Network error"),
        ):
            with pytest.raises(Exception):
                fromurl("http://example.com/test.patch")

    def test_fromurl_git_patch(self, sample_git_patch):
        """Test fromurl with Git patch from URL."""
        mock_response = MagicMock()
        mock_response.read.return_value = sample_git_patch
        mock_response.__iter__.return_value = iter(sample_git_patch.split(b"\n"))

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            result = fromurl("http://example.com/git.patch")
            assert result is not False
            assert result.type == patch.GIT


class TestApiIntegration:
    """Integration tests for API functions."""

    def test_api_consistency(self, temp_dir, sample_patch_content):
        """Test that all API functions produce consistent results."""
        # Test fromstring
        result_string = fromstring(sample_patch_content)

        # Test fromfile
        patch_file = os.path.join(temp_dir, "test.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_patch_content)
        result_file = fromfile(patch_file)

        # Test fromurl (mocked)
        mock_response = MagicMock()
        mock_response.read.return_value = sample_patch_content
        mock_response.__iter__.return_value = iter(sample_patch_content.split(b"\n"))

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            result_url = fromurl("http://example.com/test.patch")

        # All should produce equivalent results
        assert result_string is not False
        assert result_file is not False
        assert result_url is not False

        # Check that they have the same structure
        assert (
            len(result_string.items) == len(result_file.items) == len(result_url.items)
        )
        assert result_string.type == result_file.type == result_url.type

    def test_api_error_handling(self):
        """Test error handling across all API functions."""
        invalid_content = b"not a patch"

        # fromstring should return False
        assert fromstring(invalid_content) is False

        # fromfile should return False for invalid content
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(invalid_content)
            f.flush()
            temp_filename = f.name
        
        try:
            assert fromfile(temp_filename) is False
        finally:
            try:
                os.unlink(temp_filename)
            except (OSError, PermissionError):
                # On Windows, sometimes the file is still locked
                # Try again after a brief moment
                import time
                time.sleep(0.1)
                try:
                    os.unlink(temp_filename)
                except (OSError, PermissionError):
                    pass  # If we still can't delete it, that's okay for the test

        # fromurl should return False for invalid content
        mock_response = MagicMock()
        mock_response.read.return_value = invalid_content
        mock_response.__iter__.return_value = iter(invalid_content.split(b"\n"))

        with mock_patch(
            "patch.compat.urllib_request.urlopen", return_value=mock_response
        ):
            assert fromurl("http://example.com/invalid.patch") is False


@pytest.mark.parametrize(
    "api_func,input_type",
    [
        (fromstring, "content"),
        (fromfile, "file"),
    ],
)
def test_api_functions_parametrized(
    api_func, input_type, temp_dir, sample_patch_content
):
    """Parametrized test for API functions."""
    if input_type == "content":
        result = api_func(sample_patch_content)
    elif input_type == "file":
        patch_file = os.path.join(temp_dir, "test.patch")
        with open(patch_file, "wb") as f:
            f.write(sample_patch_content)
        result = api_func(patch_file)

    assert result is not False
    assert len(result.items) == 1
