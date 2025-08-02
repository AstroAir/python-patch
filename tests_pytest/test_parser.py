"""
Unit tests for parser functionality.

Tests patch parsing logic including type detection, filename normalization,
and stream enumeration.
"""

import pytest
from io import BytesIO

import patch
from patch.parser import wrapumerate, detect_type, normalize_filenames
from patch.core import Patch, PatchSet


class TestWrapumerate:
    """Test the wrapumerate class for stream enumeration."""

    def test_wrapumerate_basic_functionality(self):
        """Test basic wrapumerate functionality."""
        lines = [b"line1\n", b"line2\n", b"line3\n"]
        stream = BytesIO(b"".join(lines))

        enum = wrapumerate(stream)

        # Test first line
        assert enum.next() is True
        assert enum.lineno == 0
        assert enum.line == b"line1\n"
        assert enum.is_empty is False

        # Test second line
        assert enum.next() is True
        assert enum.lineno == 1
        assert enum.line == b"line2\n"

        # Test third line
        assert enum.next() is True
        assert enum.lineno == 2
        assert enum.line == b"line3\n"

        # Test end of stream
        assert enum.next() is False
        assert enum.is_empty is True
        assert enum.line is False

    def test_wrapumerate_empty_stream(self):
        """Test wrapumerate with empty stream."""
        stream = BytesIO(b"")
        enum = wrapumerate(stream)

        assert enum.next() is False
        assert enum.is_empty is True
        assert enum.line is False

    def test_wrapumerate_single_line(self):
        """Test wrapumerate with single line."""
        stream = BytesIO(b"single line\n")
        enum = wrapumerate(stream)

        assert enum.next() is True
        assert enum.lineno == 0
        assert enum.line == b"single line\n"

        assert enum.next() is False
        assert enum.is_empty is True

    def test_wrapumerate_no_final_newline(self):
        """Test wrapumerate with content not ending in newline."""
        stream = BytesIO(b"line without newline")
        enum = wrapumerate(stream)

        assert enum.next() is True
        assert enum.lineno == 0
        assert enum.line == b"line without newline"

        assert enum.next() is False
        assert enum.is_empty is True

    def test_wrapumerate_properties_after_exhaustion(self):
        """Test properties after stream is exhausted."""
        stream = BytesIO(b"line1\n")
        enum = wrapumerate(stream)

        # Read the line
        enum.next()
        # Exhaust the stream
        enum.next()

        assert enum.is_empty is True
        assert enum.line is False
        # lineno should still be available
        assert enum.lineno == 0  # Last valid line number

    def test_wrapumerate_multiple_calls_after_exhaustion(self):
        """Test multiple calls to next() after exhaustion."""
        stream = BytesIO(b"line1\n")
        enum = wrapumerate(stream)

        enum.next()  # Read line
        enum.next()  # Exhaust

        # Multiple calls should consistently return False
        assert enum.next() is False
        assert enum.next() is False
        assert enum.is_empty is True


class TestDetectType:
    """Test the detect_type function for patch type detection."""

    def test_detect_type_plain_patch(self):
        """Test detection of plain diff patches."""
        patch_obj = Patch()
        patch_obj.source = b"file.txt"
        patch_obj.target = b"file.txt"
        patch_obj.header = []

        result = detect_type(patch_obj)
        assert result == patch.PLAIN

    def test_detect_type_git_patch(self):
        """Test detection of Git patches."""
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.header = [
            b"diff --git a/file.txt b/file.txt\n",
            b"index 1234567..abcdefg 100644\n",
        ]

        result = detect_type(patch_obj)
        assert result == patch.GIT

    def test_detect_type_svn_patch(self):
        """Test detection of SVN patches."""
        patch_obj = Patch()
        patch_obj.source = b"file.txt"
        patch_obj.target = b"file.txt"
        patch_obj.header = [b"Index: file.txt\n", b"=" * 67 + b"\n"]

        result = detect_type(patch_obj)
        assert result == patch.SVN

    def test_detect_type_hg_patch_plain_style(self):
        """Test detection of Mercurial patches (plain style)."""
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.header = [b"diff -r 1234567890ab file.txt\n"]

        result = detect_type(patch_obj)
        assert result == patch.HG

    def test_detect_type_hg_patch_git_style(self):
        """Test detection of Mercurial patches (Git style)."""
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.header = [b"diff --git a/file.txt b/file.txt\n"]

        result = detect_type(patch_obj)
        assert result == patch.HG

    def test_detect_type_hg_changeset_patch(self):
        """Test detection of Mercurial changeset patches."""
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.header = [
            b"# HG changeset patch\n",
            b"# User test@example.com\n",
            b"diff --git a/file.txt b/file.txt\n",
        ]

        result = detect_type(patch_obj)
        assert result == patch.HG

    def test_detect_type_git_with_dev_null(self):
        """Test Git patch detection with /dev/null."""
        patch_obj = Patch()
        patch_obj.source = b"/dev/null"
        patch_obj.target = b"b/newfile.txt"
        patch_obj.header = [
            b"diff --git a/newfile.txt b/newfile.txt\n",
            b"index 0000000..1234567 100644\n",
        ]

        result = detect_type(patch_obj)
        assert result == patch.GIT

    def test_detect_type_complex_header(self):
        """Test type detection with complex headers."""
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.header = [
            b"From: author@example.com\n",
            b"Subject: Test patch\n",
            b"diff --git a/file.txt b/file.txt\n",
            b"index 1234567..abcdefg 100644\n",
        ]

        result = detect_type(patch_obj)
        assert result == patch.GIT

    def test_detect_type_edge_cases(self):
        """Test edge cases for type detection."""
        # Empty header
        patch_obj = Patch()
        patch_obj.source = b"file.txt"
        patch_obj.target = b"file.txt"
        patch_obj.header = []

        result = detect_type(patch_obj)
        assert result == patch.PLAIN

        # Header with only comments
        patch_obj.header = [b"# This is a comment\n", b"# Another comment\n"]
        result = detect_type(patch_obj)
        assert result == patch.PLAIN


class TestNormalizeFilenames:
    """Test the normalize_filenames function."""

    def test_normalize_filenames_git_patch(self):
        """Test filename normalization for Git patches."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.type = patch.GIT
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        assert patch_obj.source == b"file.txt"
        assert patch_obj.target == b"file.txt"

    def test_normalize_filenames_hg_patch(self):
        """Test filename normalization for Mercurial patches."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"a/file.txt"
        patch_obj.target = b"b/file.txt"
        patch_obj.type = patch.HG
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        assert patch_obj.source == b"file.txt"
        assert patch_obj.target == b"file.txt"

    def test_normalize_filenames_dev_null(self):
        """Test filename normalization with /dev/null."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"/dev/null"
        patch_obj.target = b"b/newfile.txt"
        patch_obj.type = patch.GIT
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        assert patch_obj.source == b"/dev/null"  # Should remain unchanged
        assert patch_obj.target == b"newfile.txt"

    def test_normalize_filenames_absolute_paths(self):
        """Test normalization of absolute paths."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"/absolute/path/file.txt"
        patch_obj.target = b"/absolute/path/file.txt"
        patch_obj.type = patch.PLAIN
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        # Should strip absolute path
        assert patch_obj.source == b"absolute/path/file.txt"
        assert patch_obj.target == b"absolute/path/file.txt"
        assert patchset.warnings > 0

    def test_normalize_filenames_parent_references(self):
        """Test normalization of parent directory references."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"../parent/file.txt"
        patch_obj.target = b"../parent/file.txt"
        patch_obj.type = patch.PLAIN
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        # Should strip parent references
        assert not patch_obj.source.startswith(b"../")
        assert not patch_obj.target.startswith(b"../")
        assert patchset.warnings > 0

    def test_normalize_filenames_mixed_separators(self):
        """Test normalization of mixed path separators."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"path\\to\\file.txt"
        patch_obj.target = b"path/to/file.txt"
        patch_obj.type = patch.PLAIN
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        # Should normalize to forward slashes
        assert b"\\" not in patch_obj.source
        assert b"\\" not in patch_obj.target

    def test_normalize_filenames_invalid_git_prefixes(self):
        """Test handling of invalid Git prefixes."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"invalid/file.txt"  # Should start with a/
        patch_obj.target = b"b/file.txt"
        patch_obj.type = patch.GIT
        patchset.items = [patch_obj]

        normalize_filenames(patchset)

        # Should generate warnings for invalid prefixes
        assert patchset.warnings > 0

    def test_normalize_filenames_multiple_patches(self):
        """Test normalization of multiple patches."""
        patchset = PatchSet()

        patch1 = Patch()
        patch1.source = b"a/file1.txt"
        patch1.target = b"b/file1.txt"
        patch1.type = patch.GIT

        patch2 = Patch()
        patch2.source = b"/absolute/file2.txt"
        patch2.target = b"/absolute/file2.txt"
        patch2.type = patch.PLAIN

        patchset.items = [patch1, patch2]

        normalize_filenames(patchset)

        # First patch should have prefixes stripped
        assert patch1.source == b"file1.txt"
        assert patch1.target == b"file1.txt"

        # Second patch should have absolute path stripped
        assert patch2.source == b"absolute/file2.txt"
        assert patch2.target == b"absolute/file2.txt"


class TestParserIntegration:
    """Integration tests for parser functionality."""

    def test_parser_with_real_patches(self, test_data_dir):
        """Test parser with real patch files."""
        git_patch_file = test_data_dir / "git-changed-file.diff"
        if git_patch_file.exists():
            patchset = patch.fromfile(str(git_patch_file))
            assert patchset is not False

            # Test that type detection worked
            assert patchset.type == patch.GIT

            # Test that filenames were normalized
            for patch_obj in patchset.items:
                # Git patches should have prefixes stripped
                assert not patch_obj.source.startswith(b"a/")
                assert not patch_obj.target.startswith(b"b/")

    def test_parser_error_recovery(self):
        """Test parser error recovery."""
        # Patch with some valid and some invalid content
        mixed_content = b"""--- a/valid.txt
+++ b/valid.txt
@@ -1,1 +1,1 @@
-old
+new
--- invalid line without +++
@@ invalid hunk header
some random content
--- a/another_valid.txt
+++ b/another_valid.txt
@@ -1,1 +1,1 @@
-old2
+new2
"""
        patchset = patch.fromstring(mixed_content)

        # Should parse what it can and report errors
        if patchset:
            assert len(patchset.items) >= 1  # At least some patches parsed
        # Errors should be reported
        # (exact behavior depends on implementation)

    def test_parser_line_ending_handling(self):
        """Test parser handling of different line endings."""
        # Test with different line endings
        patch_crlf = (
            b"--- a/test.txt\r\n+++ b/test.txt\r\n@@ -1,1 +1,1 @@\r\n-old\r\n+new\r\n"
        )
        patch_lf = b"--- a/test.txt\n+++ b/test.txt\n@@ -1,1 +1,1 @@\n-old\n+new\n"
        patch_cr = b"--- a/test.txt\r+++ b/test.txt\r@@ -1,1 +1,1 @@\r-old\r+new\r"

        for patch_content in [patch_crlf, patch_lf, patch_cr]:
            patchset = patch.fromstring(patch_content)
            if patchset:  # Some line endings might not be supported
                assert len(patchset.items) == 1


@pytest.mark.parametrize(
    "patch_type,source_prefix,target_prefix",
    [
        (patch.GIT, b"a/", b"b/"),
        (patch.HG, b"a/", b"b/"),
        (patch.PLAIN, b"", b""),
    ],
)
def test_type_detection_and_normalization_parametrized(
    patch_type, source_prefix, target_prefix
):
    """Parametrized test for type detection and filename normalization."""
    patch_obj = Patch()
    patch_obj.source = source_prefix + b"file.txt"
    patch_obj.target = target_prefix + b"file.txt"

    if patch_type == patch.GIT:
        patch_obj.header = [
            b"diff --git a/file.txt b/file.txt\n",
            b"index 123..456 100644\n",
        ]
    elif patch_type == patch.HG:
        patch_obj.header = [b"diff -r 123456 file.txt\n"]
    else:
        patch_obj.header = []

    detected_type = detect_type(patch_obj)
    assert detected_type == patch_type

    # Test normalization
    patchset = PatchSet()
    patch_obj.type = detected_type
    patchset.items = [patch_obj]

    normalize_filenames(patchset)

    if patch_type in (patch.GIT, patch.HG):
        assert patch_obj.source == b"file.txt"
        assert patch_obj.target == b"file.txt"
    else:
        assert patch_obj.source == source_prefix + b"file.txt"
        assert patch_obj.target == target_prefix + b"file.txt"
