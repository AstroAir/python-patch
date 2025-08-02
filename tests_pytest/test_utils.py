"""
Unit tests for utility functions (xisabs, xnormpath, xstrip, pathstrip).

Tests cross-platform path handling and manipulation utilities.
"""
import pytest

from patch.utils import xisabs, xnormpath, xstrip, pathstrip


class TestXisabs:
    """Test the xisabs function for cross-platform absolute path detection."""
    
    def test_xisabs_unix_absolute_paths(self):
        """Test Unix-style absolute paths."""
        assert xisabs(b'/') is True
        assert xisabs(b'/path') is True
        assert xisabs(b'/path/to/file') is True
        assert xisabs(b'/usr/local/bin') is True
    
    def test_xisabs_windows_absolute_paths(self):
        """Test Windows-style absolute paths."""
        assert xisabs(b'c:\\') is True
        assert xisabs(b'C:\\') is True
        assert xisabs(b'c:/') is True
        assert xisabs(b'C:/') is True
        assert xisabs(b'c:\\path') is True
        assert xisabs(b'C:\\path\\to\\file') is True
        assert xisabs(b'd:/path/to/file') is True
        assert xisabs(b'Z:\\') is True
    
    def test_xisabs_windows_backslash_paths(self):
        """Test Windows backslash paths."""
        assert xisabs(b'\\') is True
        assert xisabs(b'\\path') is True
        assert xisabs(b'\\\\server\\share') is True
    
    def test_xisabs_relative_paths(self):
        """Test relative paths."""
        assert xisabs(b'path') is False
        assert xisabs(b'path/to/file') is False
        assert xisabs(b'./path') is False
        assert xisabs(b'../path') is False
        assert xisabs(b'path\\to\\file') is False
        assert xisabs(b'.\\path') is False
        assert xisabs(b'..\\path') is False
    
    def test_xisabs_edge_cases(self):
        """Test edge cases for xisabs."""
        assert xisabs(b'') is False
        assert xisabs(b'c:') is False  # Drive letter without separator
        assert xisabs(b'c') is False
        assert xisabs(b':') is False
        assert xisabs(b'path:') is False
        assert xisabs(b'path:\\') is False
        assert xisabs(b'path:/') is False
    
    def test_xisabs_mixed_separators(self):
        """Test paths with mixed separators."""
        assert xisabs(b'c:\\path/to/file') is True
        assert xisabs(b'c:/path\\to\\file') is True
    
    @pytest.mark.parametrize("path,expected", [
        (b'/', True),
        (b'/path', True),
        (b'c:\\', True),
        (b'c:/', True),
        (b'\\', True),
        (b'path', False),
        (b'./path', False),
        (b'', False),
    ])
    def test_xisabs_parametrized(self, path, expected):
        """Parametrized test for xisabs."""
        assert xisabs(path) == expected


class TestXnormpath:
    """Test the xnormpath function for cross-platform path normalization."""
    
    def test_xnormpath_basic_normalization(self):
        """Test basic path normalization."""
        assert xnormpath(b'path/to/file') == b'path/to/file'
        assert xnormpath(b'path\\to\\file') == b'path/to/file'
        assert xnormpath(b'path/to/../file') == b'path/file'
        assert xnormpath(b'path/./file') == b'path/file'
    
    def test_xnormpath_complex_paths(self):
        """Test complex path normalization."""
        assert xnormpath(b'../something/..\\..\\file.to.patch') == b'../../file.to.patch'
        assert xnormpath(b'path/../other/../final') == b'final'
        assert xnormpath(b'./path/./to/./file') == b'path/to/file'
    
    def test_xnormpath_multiple_separators(self):
        """Test normalization of multiple separators."""
        assert xnormpath(b'path//to//file') == b'path/to/file'
        assert xnormpath(b'path\\\\to\\\\file') == b'path/to/file'
        assert xnormpath(b'path/\\to/\\file') == b'path/to/file'
    
    def test_xnormpath_root_paths(self):
        """Test normalization of root paths."""
        assert xnormpath(b'/') == b'/'
        assert xnormpath(b'\\') == b'/'
        assert xnormpath(b'/path/../..') == b'/'
    
    def test_xnormpath_empty_and_current(self):
        """Test normalization of empty and current directory paths."""
        assert xnormpath(b'') == b'.'
        assert xnormpath(b'.') == b'.'
        assert xnormpath(b'./') == b'.'
        assert xnormpath(b'.\\') == b'.'
    
    def test_xnormpath_preserves_leading_dots(self):
        """Test that leading .. are preserved when appropriate."""
        assert xnormpath(b'../path') == b'../path'
        assert xnormpath(b'../../path') == b'../../path'
        assert xnormpath(b'../path/../other') == b'../other'
    
    @pytest.mark.parametrize("input_path,expected", [
        (b'path/to/file', b'path/to/file'),
        (b'path\\to\\file', b'path/to/file'),
        (b'path/../file', b'file'),
        (b'path/./file', b'path/file'),
        (b'../something/..\\..\\file.to.patch', b'../../file.to.patch'),
        (b'', b'.'),
        (b'.', b'.'),
    ])
    def test_xnormpath_parametrized(self, input_path, expected):
        """Parametrized test for xnormpath."""
        assert xnormpath(input_path) == expected


class TestXstrip:
    """Test the xstrip function for stripping absolute path prefixes."""
    
    def test_xstrip_unix_absolute_paths(self):
        """Test stripping Unix absolute paths."""
        assert xstrip(b'/') == b''
        assert xstrip(b'/path') == b'path'
        assert xstrip(b'/path/to/file') == b'path/to/file'
        assert xstrip(b'/usr/local/bin') == b'usr/local/bin'
    
    def test_xstrip_windows_absolute_paths(self):
        """Test stripping Windows absolute paths."""
        assert xstrip(b'c:\\') == b''
        assert xstrip(b'C:\\') == b''
        assert xstrip(b'c:/') == b''
        assert xstrip(b'C:/') == b''
        assert xstrip(b'c:\\path') == b'path'
        assert xstrip(b'C:\\path\\to\\file') == b'path\\to\\file'
        assert xstrip(b'd:/path/to/file') == b'path/to/file'
    
    def test_xstrip_windows_backslash_paths(self):
        """Test stripping Windows backslash paths."""
        assert xstrip(b'\\') == b''
        assert xstrip(b'\\path') == b'path'
        assert xstrip(b'\\\\server\\share') == b'server\\share'
    
    def test_xstrip_relative_paths_unchanged(self):
        """Test that relative paths are not changed."""
        assert xstrip(b'path') == b'path'
        assert xstrip(b'path/to/file') == b'path/to/file'
        assert xstrip(b'./path') == b'./path'
        assert xstrip(b'../path') == b'../path'
        assert xstrip(b'path\\to\\file') == b'path\\to\\file'
    
    def test_xstrip_multiple_absolute_components(self):
        """Test stripping multiple absolute components."""
        # The function should strip until no absolute components remain
        assert xstrip(b'///path') == b'path'
        assert xstrip(b'\\\\\\path') == b'path'
        assert xstrip(b'c:\\\\path') == b'path'
    
    def test_xstrip_edge_cases(self):
        """Test edge cases for xstrip."""
        assert xstrip(b'') == b''
        assert xstrip(b'c:') == b'c:'  # Not absolute without separator
        assert xstrip(b'path:') == b'path:'
    
    @pytest.mark.parametrize("input_path,expected", [
        (b'/', b''),
        (b'/path', b'path'),
        (b'c:\\', b''),
        (b'c:/path', b'path'),
        (b'\\', b''),
        (b'\\path', b'path'),
        (b'path', b'path'),
        (b'./path', b'./path'),
        (b'', b''),
    ])
    def test_xstrip_parametrized(self, input_path, expected):
        """Parametrized test for xstrip."""
        assert xstrip(input_path) == expected


class TestPathstrip:
    """Test the pathstrip function for stripping leading path components."""
    
    def test_pathstrip_basic_functionality(self):
        """Test basic pathstrip functionality."""
        assert pathstrip(b'path/to/test/name.diff', 0) == b'path/to/test/name.diff'
        assert pathstrip(b'path/to/test/name.diff', 1) == b'to/test/name.diff'
        assert pathstrip(b'path/to/test/name.diff', 2) == b'test/name.diff'
        assert pathstrip(b'path/to/test/name.diff', 3) == b'name.diff'
    
    def test_pathstrip_single_component(self):
        """Test pathstrip with single path component."""
        assert pathstrip(b'filename.txt', 0) == b'filename.txt'
        assert pathstrip(b'filename.txt', 1) == b'filename.txt'  # Can't strip more than available
    
    def test_pathstrip_strip_all_components(self):
        """Test stripping all path components."""
        assert pathstrip(b'path/name.diff', 1) == b'name.diff'
        assert pathstrip(b'path/name.diff', 2) == b'name.diff'  # Can't strip more than available
        assert pathstrip(b'path/name.diff', 10) == b'name.diff'  # Large number
    
    def test_pathstrip_windows_paths(self):
        """Test pathstrip with Windows-style paths."""
        # Note: pathstrip uses os.path.split which handles platform-specific separators
        # But the function normalizes to forward slashes in output
        result = pathstrip(b'path\\to\\test\\name.diff', 2)
        # The exact result depends on the platform, but should strip 2 components
        assert b'name.diff' in result or b'test/name.diff' in result
    
    def test_pathstrip_empty_path(self):
        """Test pathstrip with empty path."""
        assert pathstrip(b'', 0) == b''
        assert pathstrip(b'', 1) == b''
    
    def test_pathstrip_root_path(self):
        """Test pathstrip with root paths."""
        # This tests the edge case where dirname returns empty string
        result = pathstrip(b'filename', 0)
        assert result == b'filename'
    
    @pytest.mark.parametrize("path,n,expected", [
        (b'path/to/test/name.diff', 0, b'path/to/test/name.diff'),
        (b'path/to/test/name.diff', 1, b'to/test/name.diff'),
        (b'path/to/test/name.diff', 2, b'test/name.diff'),
        (b'path/name.diff', 1, b'name.diff'),
        (b'name.diff', 0, b'name.diff'),
        (b'name.diff', 1, b'name.diff'),
    ])
    def test_pathstrip_parametrized(self, path, n, expected):
        """Parametrized test for pathstrip."""
        result = pathstrip(path, n)
        assert result == expected


class TestUtilsIntegration:
    """Integration tests for utility functions."""
    
    def test_utils_workflow(self):
        """Test a typical workflow using multiple utility functions."""
        # Start with a complex absolute path
        path = b'c:\\some\\..\\complex\\path\\..\\to\\file.txt'
        
        # Normalize it
        normalized = xnormpath(path)
        assert b'file.txt' in normalized
        
        # Check if it's absolute
        is_abs = xisabs(normalized)
        
        # Strip absolute components if needed
        if is_abs:
            stripped = xstrip(normalized)
        else:
            stripped = normalized
        
        # Strip leading path components
        final = pathstrip(stripped, 1)
        
        # Should end up with a clean relative path
        assert b'file.txt' in final
    
    def test_cross_platform_consistency(self, cross_platform_paths):
        """Test that utilities work consistently across platforms."""
        # Test absolute path detection
        for abs_path in cross_platform_paths['absolute_unix'] + cross_platform_paths['absolute_windows']:
            assert xisabs(abs_path) is True
        
        for rel_path in cross_platform_paths['relative']:
            assert xisabs(rel_path) is False
        
        # Test normalization
        for mixed_path in cross_platform_paths['mixed']:
            normalized = xnormpath(mixed_path)
            # Should not contain backslashes in output
            assert b'\\' not in normalized or b'/' in normalized
        
        # Test stripping
        for abs_path in cross_platform_paths['absolute_unix'] + cross_platform_paths['absolute_windows']:
            if abs_path != b'/':  # Root path becomes empty
                stripped = xstrip(abs_path)
                # Should not be absolute after stripping
                assert not xisabs(stripped) or stripped == b''


class TestUtilsErrorHandling:
    """Test error handling and edge cases for utility functions."""
    
    def test_utils_with_none_input(self):
        """Test utility functions with None input."""
        with pytest.raises((TypeError, AttributeError)):
            xisabs(None)
        
        with pytest.raises((TypeError, AttributeError)):
            xnormpath(None)
        
        with pytest.raises((TypeError, AttributeError)):
            xstrip(None)
        
        with pytest.raises((TypeError, AttributeError)):
            pathstrip(None, 1)
    
    def test_utils_with_string_input(self):
        """Test utility functions with string input (should work with bytes)."""
        # These functions expect bytes, but let's see how they handle strings
        try:
            result = xisabs('path')
            # If it works, it should return a boolean
            assert isinstance(result, bool)
        except (TypeError, AttributeError):
            # It's okay if it raises an error for wrong type
            pass
    
    def test_pathstrip_negative_n(self):
        """Test pathstrip with negative n value."""
        # Should handle gracefully
        result = pathstrip(b'path/to/file', -1)
        # Should return the original path or handle gracefully
        assert isinstance(result, bytes)
