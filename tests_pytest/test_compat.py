"""
Unit tests for compatibility layer.

Tests Python 2/3 compatibility utilities including string handling
and import compatibility.
"""

import pytest
import sys

from patch.compat import StringIO, urllib_request, PY3K, compat_next, tostr


class TestPythonVersionDetection:
    """Test Python version detection."""

    def test_py3k_detection(self):
        """Test PY3K constant reflects current Python version."""
        if sys.version_info >= (3, 0):
            assert PY3K is True
        else:
            assert PY3K is False

    def test_py3k_is_boolean(self):
        """Test that PY3K is a boolean value."""
        assert isinstance(PY3K, bool)


class TestStringIO:
    """Test StringIO compatibility."""

    def test_stringio_creation(self):
        """Test StringIO object creation."""
        sio = StringIO()
        assert sio is not None

    def test_stringio_with_bytes(self):
        """Test StringIO with bytes content."""
        content = b"test content\nline 2\n"
        sio = StringIO(content)

        # Should be able to read content
        read_content = sio.read()
        assert read_content == content

    def test_stringio_readline(self):
        """Test StringIO readline functionality."""
        content = b"line 1\nline 2\nline 3\n"
        sio = StringIO(content)

        line1 = sio.readline()
        line2 = sio.readline()
        line3 = sio.readline()

        assert line1 == b"line 1\n"
        assert line2 == b"line 2\n"
        assert line3 == b"line 3\n"

    def test_stringio_iteration(self):
        """Test StringIO iteration."""
        content = b"line 1\nline 2\nline 3\n"
        sio = StringIO(content)

        lines = list(sio)
        assert len(lines) == 3
        assert lines[0] == b"line 1\n"
        assert lines[1] == b"line 2\n"
        assert lines[2] == b"line 3\n"

    def test_stringio_seek_tell(self):
        """Test StringIO seek and tell functionality."""
        content = b"test content"
        sio = StringIO(content)

        # Read some content
        sio.read(4)
        pos = sio.tell()
        assert pos == 4

        # Seek back to beginning
        sio.seek(0)
        assert sio.tell() == 0

        # Read all content
        read_content = sio.read()
        assert read_content == content

    def test_stringio_empty(self):
        """Test StringIO with empty content."""
        sio = StringIO(b"")
        assert sio.read() == b""
        assert sio.readline() == b""
        assert list(sio) == []


class TestUrllibRequest:
    """Test urllib_request compatibility."""

    def test_urllib_request_import(self):
        """Test that urllib_request is importable."""
        assert urllib_request is not None

    def test_urllib_request_has_urlopen(self):
        """Test that urllib_request has urlopen function."""
        assert hasattr(urllib_request, "urlopen")
        assert callable(urllib_request.urlopen)

    def test_urllib_request_urlopen_signature(self):
        """Test that urlopen has expected signature."""
        # This is a basic test - we won't actually make network calls
        import inspect

        sig = inspect.signature(urllib_request.urlopen)

        # Should have at least a url parameter
        params = list(sig.parameters.keys())
        assert len(params) >= 1
        # First parameter should be url-like
        assert "url" in params[0].lower() or params[0] in ["url", "fullurl", "req"]


class TestCompatNext:
    """Test compat_next function."""

    def test_compat_next_with_generator(self):
        """Test compat_next with generator."""

        def test_generator():
            yield 1
            yield 2
            yield 3

        gen = test_generator()

        assert compat_next(gen) == 1
        assert compat_next(gen) == 2
        assert compat_next(gen) == 3

        # Should raise StopIteration when exhausted
        with pytest.raises(StopIteration):
            compat_next(gen)

    def test_compat_next_with_iterator(self):
        """Test compat_next with iterator."""
        items = [1, 2, 3]
        iterator = iter(items)

        assert compat_next(iterator) == 1
        assert compat_next(iterator) == 2
        assert compat_next(iterator) == 3

        with pytest.raises(StopIteration):
            compat_next(iterator)

    def test_compat_next_with_enumerate(self):
        """Test compat_next with enumerate object."""
        items = ["a", "b", "c"]
        enum = enumerate(items)

        assert compat_next(enum) == (0, "a")
        assert compat_next(enum) == (1, "b")
        assert compat_next(enum) == (2, "c")

        with pytest.raises(StopIteration):
            compat_next(enum)

    def test_compat_next_empty_iterator(self):
        """Test compat_next with empty iterator."""
        empty_iter = iter([])

        with pytest.raises(StopIteration):
            compat_next(empty_iter)

    def test_compat_next_with_file_like_object(self):
        """Test compat_next with file-like object."""
        content = b"line1\nline2\nline3\n"
        sio = StringIO(content)

        # StringIO should be iterable
        assert compat_next(iter(sio)) == b"line1\n"


class TestTostr:
    """Test tostr function for bytes to string conversion."""

    def test_tostr_with_bytes(self):
        """Test tostr with bytes input."""
        test_bytes = b"hello world"
        result = tostr(test_bytes)

        if PY3K:
            # In Python 3, should decode to string
            assert isinstance(result, str)
            assert result == "hello world"
        else:
            # In Python 2, should return bytes unchanged
            assert isinstance(result, bytes)
            assert result == test_bytes

    def test_tostr_with_utf8_bytes(self):
        """Test tostr with UTF-8 encoded bytes."""
        # UTF-8 encoded string with special characters
        test_bytes = "héllo wörld".encode("utf-8")
        result = tostr(test_bytes)

        if PY3K:
            assert isinstance(result, str)
            assert result == "héllo wörld"
        else:
            assert isinstance(result, bytes)
            assert result == test_bytes

    def test_tostr_with_empty_bytes(self):
        """Test tostr with empty bytes."""
        test_bytes = b""
        result = tostr(test_bytes)

        if PY3K:
            assert isinstance(result, str)
            assert result == ""
        else:
            assert isinstance(result, bytes)
            assert result == test_bytes

    def test_tostr_with_newlines(self):
        """Test tostr with bytes containing newlines."""
        test_bytes = b"line1\nline2\r\nline3\r"
        result = tostr(test_bytes)

        if PY3K:
            assert isinstance(result, str)
            assert "line1" in result
            assert "line2" in result
            assert "line3" in result
        else:
            assert isinstance(result, bytes)
            assert result == test_bytes

    def test_tostr_with_binary_data(self):
        """Test tostr with binary data that might not be valid UTF-8."""
        # Some binary data that might not be valid UTF-8
        test_bytes = b"\x00\x01\x02\xff\xfe"

        if PY3K:
            # Should handle gracefully (might raise exception or return replacement chars)
            try:
                result = tostr(test_bytes)
                assert isinstance(result, str)
            except UnicodeDecodeError:
                # It's acceptable to raise an exception for invalid UTF-8
                pass
        else:
            result = tostr(test_bytes)
            assert isinstance(result, bytes)
            assert result == test_bytes

    @pytest.mark.parametrize(
        "input_bytes,expected_str",
        [
            (b"simple", "simple"),
            (b"with spaces", "with spaces"),
            (b"123456", "123456"),
            (b"", ""),
        ],
    )
    def test_tostr_parametrized(self, input_bytes, expected_str):
        """Parametrized test for tostr function."""
        result = tostr(input_bytes)

        if PY3K:
            assert isinstance(result, str)
            assert result == expected_str
        else:
            assert isinstance(result, bytes)
            assert result == input_bytes


class TestCompatibilityIntegration:
    """Integration tests for compatibility utilities."""

    def test_stringio_with_patch_parsing(self):
        """Test StringIO compatibility with patch parsing workflow."""
        patch_content = b"""--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
"""

        # Create StringIO object
        sio = StringIO(patch_content)

        # Should be usable for iteration (like in patch parsing)
        lines = []
        for line in sio:
            lines.append(line)

        assert len(lines) == 7  # Number of lines in patch
        assert lines[0] == b"--- a/test.txt\n"
        assert lines[1] == b"+++ b/test.txt\n"

    def test_compat_next_with_stringio(self):
        """Test compat_next with StringIO iterator."""
        content = b"line1\nline2\nline3\n"
        sio = StringIO(content)
        iterator = iter(sio)

        line1 = compat_next(iterator)
        line2 = compat_next(iterator)
        line3 = compat_next(iterator)

        assert line1 == b"line1\n"
        assert line2 == b"line2\n"
        assert line3 == b"line3\n"

        with pytest.raises(StopIteration):
            compat_next(iterator)

    def test_tostr_with_filename_display(self):
        """Test tostr for filename display (common use case)."""
        # Simulate filenames that might contain non-ASCII characters
        filenames = [
            b"simple.txt",
            b"file with spaces.txt",
            b"caf\xc3\xa9.txt",  # café in UTF-8
        ]

        for filename in filenames:
            result = tostr(filename)

            if PY3K:
                assert isinstance(result, str)
                # Should be displayable
                assert len(result) > 0
            else:
                assert isinstance(result, bytes)
                assert result == filename

    def test_cross_python_version_consistency(self):
        """Test that compatibility layer provides consistent interface."""
        # Test that all compatibility utilities are available
        assert StringIO is not None
        assert urllib_request is not None
        assert compat_next is not None
        assert tostr is not None
        assert isinstance(PY3K, bool)

        # Test basic functionality works regardless of Python version
        sio = StringIO(b"test")
        assert sio.read() == b"test"

        iterator = iter([1, 2, 3])
        assert compat_next(iterator) == 1

        result = tostr(b"test")
        assert result is not None


class TestCompatibilityErrorHandling:
    """Test error handling in compatibility utilities."""

    def test_compat_next_with_invalid_object(self):
        """Test compat_next with non-iterable object."""
        with pytest.raises((TypeError, AttributeError)):
            compat_next(42)  # Integer is not iterable

    def test_tostr_with_none(self):
        """Test tostr with None input."""
        with pytest.raises((TypeError, AttributeError)):
            tostr(None)

    def test_stringio_with_invalid_input(self):
        """Test StringIO with invalid input types."""
        # StringIO should handle bytes, but let's test edge cases
        try:
            # This might work or might not, depending on implementation
            sio = StringIO(None)
        except (TypeError, ValueError):
            # It's acceptable to raise an exception
            pass

    def test_compatibility_with_different_encodings(self):
        """Test compatibility utilities with different encodings."""
        # Test with different encoded strings
        test_strings = [
            "hello".encode("utf-8"),
            "hello".encode("ascii"),
        ]

        if sys.version_info >= (3, 0):
            # Add more encodings for Python 3
            test_strings.extend(
                [
                    "héllo".encode("utf-8"),
                    "hello".encode("latin-1"),
                ]
            )

        for encoded_str in test_strings:
            # tostr should handle these gracefully
            try:
                result = tostr(encoded_str)
                if PY3K:
                    assert isinstance(result, str)
                else:
                    assert isinstance(result, bytes)
            except UnicodeDecodeError:
                # Some encodings might not be decodable as UTF-8
                pass
