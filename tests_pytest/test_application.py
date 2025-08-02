"""
Unit tests for application functionality.

Tests patch application logic including apply, revert, diffstat,
file matching, and stream processing.
"""

import os
from io import BytesIO

import patch
from patch.application import (
    diffstat,
    findfile,
    can_patch,
    match_file_hunks,
    patch_stream,
    write_hunks,
    reverse_patchset,
    dump_patchset,
)
from patch.core import Hunk, Patch, PatchSet


class TestDiffstat:
    """Test the diffstat function."""

    def test_diffstat_single_file(self):
        """Test diffstat for a single file patch."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.target = b"test.txt"

        hunk = Hunk()
        hunk.text = [
            b" unchanged line\n",
            b"-removed line\n",
            b"+added line\n",
            b" another unchanged\n",
        ]
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = diffstat(patchset)

        assert "test.txt" in result
        assert "1 +" in result or "1 insertions" in result
        assert "1 -" in result or "1 deletions" in result
        assert "1 files changed" in result

    def test_diffstat_multiple_files(self):
        """Test diffstat for multiple files."""
        patchset = PatchSet()

        # First file
        patch1 = Patch()
        patch1.target = b"file1.txt"
        hunk1 = Hunk()
        hunk1.text = [b"+added line 1\n", b"+added line 2\n"]
        patch1.hunks = [hunk1]

        # Second file
        patch2 = Patch()
        patch2.target = b"file2.txt"
        hunk2 = Hunk()
        hunk2.text = [b"-removed line\n"]
        patch2.hunks = [hunk2]

        patchset.items = [patch1, patch2]

        result = diffstat(patchset)

        assert "file1.txt" in result
        assert "file2.txt" in result
        assert "2 files changed" in result

    def test_diffstat_no_changes(self):
        """Test diffstat with no actual changes."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.target = b"test.txt"

        hunk = Hunk()
        hunk.text = [b" unchanged line 1\n", b" unchanged line 2\n"]
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = diffstat(patchset)

        assert "test.txt" in result
        assert "0 +" in result or "0 insertions" in result
        assert "0 -" in result or "0 deletions" in result

    def test_diffstat_large_changes(self):
        """Test diffstat with large number of changes."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.target = b"large_file.txt"

        hunk = Hunk()
        # Create many changes
        hunk.text = [b"+added line\n"] * 50 + [b"-removed line\n"] * 30
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = diffstat(patchset)

        assert "large_file.txt" in result
        assert "50" in result  # Should show insertion count
        assert "30" in result  # Should show deletion count

    def test_diffstat_histogram_scaling(self):
        """Test that diffstat histogram scales properly."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.target = b"test.txt"

        hunk = Hunk()
        # Create changes that would exceed normal histogram width
        hunk.text = [b"+added line\n"] * 100
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = diffstat(patchset)

        # Should contain histogram characters
        assert "+" in result
        # Should not be excessively long
        lines = result.split("\n")
        for line in lines:
            if "test.txt" in line:
                assert len(line) < 200  # Reasonable line length


class TestFindfile:
    """Test the findfile function."""

    def test_findfile_old_exists(self, temp_dir):
        """Test findfile when old file exists."""
        old_file = os.path.join(temp_dir, "old.txt")
        new_file = os.path.join(temp_dir, "new.txt")

        with open(old_file, "w") as f:
            f.write("content")

        result = findfile(old_file.encode(), new_file.encode())
        assert result == old_file.encode()

    def test_findfile_new_exists(self, temp_dir):
        """Test findfile when new file exists."""
        old_file = os.path.join(temp_dir, "old.txt")
        new_file = os.path.join(temp_dir, "new.txt")

        with open(new_file, "w") as f:
            f.write("content")

        result = findfile(old_file.encode(), new_file.encode())
        assert result == new_file.encode()

    def test_findfile_both_exist(self, temp_dir):
        """Test findfile when both files exist (should prefer old)."""
        old_file = os.path.join(temp_dir, "old.txt")
        new_file = os.path.join(temp_dir, "new.txt")

        with open(old_file, "w") as f:
            f.write("old content")
        with open(new_file, "w") as f:
            f.write("new content")

        result = findfile(old_file.encode(), new_file.encode())
        assert result == old_file.encode()

    def test_findfile_neither_exists(self, temp_dir):
        """Test findfile when neither file exists."""
        old_file = os.path.join(temp_dir, "nonexistent_old.txt")
        new_file = os.path.join(temp_dir, "nonexistent_new.txt")

        result = findfile(old_file.encode(), new_file.encode())
        assert result is None

    def test_findfile_google_code_workaround(self, temp_dir):
        """Test findfile with Google Code prefix workaround."""
        # Create files without a/ b/ prefixes
        actual_file = os.path.join(temp_dir, "file.txt")
        with open(actual_file, "w") as f:
            f.write("content")

        # Try to find with a/ b/ prefixes
        old_file = b"a/" + actual_file.encode()
        new_file = b"b/" + actual_file.encode()

        result = findfile(old_file, new_file)

        # Should find the actual file after stripping prefixes
        assert result == actual_file.encode()


class TestCanPatch:
    """Test the can_patch function."""

    def test_can_patch_matching_file(self, temp_dir, sample_file_content):
        """Test can_patch with matching file content."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(sample_file_content)

        # Create a patchset that matches the file
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = test_file.encode()

        hunk = Hunk()
        hunk.starttgt = 1
        hunk.text = [b" line1\n", b" line2\n", b" line3\n"]
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = can_patch(patchset, test_file)
        assert result is True

    def test_can_patch_non_matching_file(self, temp_dir):
        """Test can_patch with non-matching file content."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "wb") as f:
            f.write(b"different content\n")

        # Create a patchset that doesn't match
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = test_file.encode()

        hunk = Hunk()
        hunk.starttgt = 1
        hunk.text = [b" expected content\n"]
        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        result = can_patch(patchset, test_file)
        assert result is False

    def test_can_patch_file_not_in_patchset(self, temp_dir):
        """Test can_patch with file not in patchset."""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("content")

        patchset = PatchSet()
        # Empty patchset

        result = can_patch(patchset, test_file)
        assert result is None


class TestMatchFileHunks:
    """Test the match_file_hunks function."""

    def test_match_file_hunks_success(self, temp_dir):
        """Test successful hunk matching."""
        test_file = os.path.join(temp_dir, "test.txt")
        content = b"line1\nline2\nline3\n"
        with open(test_file, "wb") as f:
            f.write(content)

        hunk = Hunk()
        hunk.starttgt = 1
        hunk.text = [b" line1\n", b" line2\n", b" line3\n"]

        result = match_file_hunks(test_file, [hunk])
        assert result is True

    def test_match_file_hunks_failure(self, temp_dir):
        """Test failed hunk matching."""
        test_file = os.path.join(temp_dir, "test.txt")
        content = b"line1\nline2\nline3\n"
        with open(test_file, "wb") as f:
            f.write(content)

        hunk = Hunk()
        hunk.starttgt = 1
        hunk.text = [b" different\n", b" content\n"]

        result = match_file_hunks(test_file, [hunk])
        assert result is False

    def test_match_file_hunks_premature_eof(self, temp_dir):
        """Test hunk matching with premature EOF."""
        test_file = os.path.join(temp_dir, "test.txt")
        content = b"line1\n"  # Short file
        with open(test_file, "wb") as f:
            f.write(content)

        hunk = Hunk()
        hunk.starttgt = 1
        hunk.text = [b" line1\n", b" line2\n", b" line3\n"]  # Expects more lines

        result = match_file_hunks(test_file, [hunk])
        assert result is False


class TestPatchStream:
    """Test the patch_stream function."""

    def test_patch_stream_basic(self, sample_file_content):
        """Test basic patch stream functionality."""
        input_stream = BytesIO(sample_file_content)

        hunk = Hunk()
        hunk.startsrc = 2
        hunk.text = [b" line1\n", b"-line2\n", b"+line2_modified\n", b" line3\n"]

        result = list(patch_stream(input_stream, [hunk]))

        # Should yield modified content
        assert b"line1\n" in result
        assert b"line2_modified\n" in result
        assert b"line3\n" in result
        assert b"line2\n" not in result  # Original line2 should be removed

    def test_patch_stream_addition(self):
        """Test patch stream with line additions."""
        input_stream = BytesIO(b"line1\nline3\n")

        hunk = Hunk()
        hunk.startsrc = 1
        hunk.text = [b" line1\n", b"+line2\n", b" line3\n"]

        result = list(patch_stream(input_stream, [hunk]))

        # Should have added line2
        content = b"".join(result)
        assert b"line1\nline2\nline3\n" == content

    def test_patch_stream_deletion(self):
        """Test patch stream with line deletions."""
        input_stream = BytesIO(b"line1\nline2\nline3\n")

        hunk = Hunk()
        hunk.startsrc = 1
        hunk.text = [b" line1\n", b"-line2\n", b" line3\n"]

        result = list(patch_stream(input_stream, [hunk]))

        # Should have removed line2
        content = b"".join(result)
        assert b"line1\nline3\n" == content

    def test_patch_stream_line_ending_detection(self):
        """Test patch stream line ending detection and conversion."""
        # Input with CRLF
        input_stream = BytesIO(b"line1\r\nline2\r\nline3\r\n")

        hunk = Hunk()
        hunk.startsrc = 2
        hunk.text = [b" line1\n", b"-line2\n", b"+modified\n", b" line3\n"]

        result = list(patch_stream(input_stream, [hunk]))

        # Should preserve line endings
        content = b"".join(result)
        assert b"\r\n" in content  # Should maintain CRLF


class TestWriteHunks:
    """Test the write_hunks function."""

    def test_write_hunks_basic(self, temp_dir, sample_file_content):
        """Test basic write_hunks functionality."""
        src_file = os.path.join(temp_dir, "source.txt")
        tgt_file = os.path.join(temp_dir, "target.txt")

        with open(src_file, "wb") as f:
            f.write(sample_file_content)

        hunk = Hunk()
        hunk.startsrc = 2
        hunk.text = [b" line1\n", b"-line2\n", b"+line2_modified\n", b" line3\n"]

        result = write_hunks(src_file, tgt_file, [hunk])
        assert result is True

        # Check target file content
        with open(tgt_file, "rb") as f:
            content = f.read()

        assert b"line1\n" in content
        assert b"line2_modified\n" in content
        assert b"line3\n" in content
        assert b"line2\n" not in content

    def test_write_hunks_permissions(self, temp_dir, sample_file_content):
        """Test that write_hunks preserves file permissions."""
        src_file = os.path.join(temp_dir, "source.txt")
        tgt_file = os.path.join(temp_dir, "target.txt")

        with open(src_file, "wb") as f:
            f.write(sample_file_content)

        # Set specific permissions
        os.chmod(src_file, 0o644)

        hunk = Hunk()
        hunk.startsrc = 1
        hunk.text = [b" line1\n", b" line2\n", b" line3\n"]

        write_hunks(src_file, tgt_file, [hunk])

        # Check that permissions were copied
        src_stat = os.stat(src_file)
        tgt_stat = os.stat(tgt_file)
        assert src_stat.st_mode == tgt_stat.st_mode


class TestReversePatchset:
    """Test the reverse_patchset function."""

    def test_reverse_patchset_basic(self):
        """Test basic patchset reversal."""
        patchset = PatchSet()
        patch_obj = Patch()

        hunk = Hunk()
        hunk.startsrc = 10
        hunk.starttgt = 15
        hunk.linessrc = 5
        hunk.linestgt = 7
        hunk.text = [b" context\n", b"-removed\n", b"+added\n"]

        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        reverse_patchset(patchset)

        # Check that hunk was reversed
        assert hunk.startsrc == 15  # Swapped
        assert hunk.starttgt == 10  # Swapped
        assert hunk.linessrc == 7  # Swapped
        assert hunk.linestgt == 5  # Swapped

        # Check that +/- were swapped
        assert hunk.text[1] == b"+removed\n"  # Was -removed
        assert hunk.text[2] == b"-added\n"  # Was +added

    def test_reverse_patchset_context_unchanged(self):
        """Test that context lines remain unchanged during reversal."""
        patchset = PatchSet()
        patch_obj = Patch()

        hunk = Hunk()
        hunk.text = [b" context1\n", b" context2\n", b"-removed\n", b" context3\n"]

        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        reverse_patchset(patchset)

        # Context lines should be unchanged
        assert hunk.text[0] == b" context1\n"
        assert hunk.text[1] == b" context2\n"
        assert hunk.text[3] == b" context3\n"
        # Only the - line should become +
        assert hunk.text[2] == b"+removed\n"


class TestDumpPatchset:
    """Test the dump_patchset function."""

    def test_dump_patchset_basic(self, capsys):
        """Test basic patchset dumping."""
        patchset = PatchSet()
        patch_obj = Patch()
        patch_obj.source = b"old.txt"
        patch_obj.target = b"new.txt"
        patch_obj.header = [b"Header line 1\n", b"Header line 2\n"]

        hunk = Hunk()
        hunk.startsrc = 1
        hunk.linessrc = 3
        hunk.starttgt = 1
        hunk.linestgt = 3
        hunk.text = [b" line1\n", b"-line2\n", b"+modified\n"]

        patch_obj.hunks = [hunk]
        patchset.items = [patch_obj]

        dump_patchset(patchset)

        captured = capsys.readouterr()
        output = captured.out

        assert "Header line 1" in output
        assert "Header line 2" in output
        assert "--- old.txt" in output
        assert "+++ new.txt" in output
        assert "@@ -1,3 +1,3 @@" in output
        assert " line1" in output
        assert "-line2" in output
        assert "+modified" in output


class TestApplicationIntegration:
    """Integration tests for application functionality."""

    def test_full_patch_application_workflow(
        self,
        temp_dir,
        sample_patch_content,
        sample_file_content,
        expected_patched_content,
    ):
        """Test complete patch application workflow."""
        # Create source file
        src_file = os.path.join(temp_dir, "test.txt")
        with open(src_file, "wb") as f:
            f.write(sample_file_content)

        # Parse patch
        patchset = patch.fromstring(sample_patch_content)
        assert patchset is not False

        # Apply patch
        result = patchset.apply(root=temp_dir)
        assert result is True

        # Check result
        with open(src_file, "rb") as f:
            content = f.read()

        assert content == expected_patched_content

    def test_patch_revert_workflow(
        self,
        temp_dir,
        sample_patch_content,
        sample_file_content,
        expected_patched_content,
    ):
        """Test patch application and revert workflow."""
        # Create source file
        src_file = os.path.join(temp_dir, "test.txt")
        with open(src_file, "wb") as f:
            f.write(sample_file_content)

        # Parse and apply patch
        patchset = patch.fromstring(sample_patch_content)
        patchset.apply(root=temp_dir)

        # Verify patch was applied
        with open(src_file, "rb") as f:
            content = f.read()
        assert content == expected_patched_content

        # Revert patch
        result = patchset.revert(root=temp_dir)
        assert result is True

        # Verify revert worked
        with open(src_file, "rb") as f:
            content = f.read()
        assert content == sample_file_content
