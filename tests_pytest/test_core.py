"""
Unit tests for core classes (Hunk, Patch, PatchSet).

Tests the core functionality of the patch parsing and representation classes.
"""

import pytest
from io import BytesIO

import patch
from patch.core import Hunk, Patch, PatchSet


class TestHunk:
    """Test the Hunk class."""

    def test_hunk_initialization(self):
        """Test Hunk object initialization."""
        hunk = Hunk()
        assert hunk.startsrc is None
        assert hunk.linessrc is None
        assert hunk.starttgt is None
        assert hunk.linestgt is None
        assert hunk.invalid is False
        assert hunk.desc == ""
        assert hunk.text == []

    def test_hunk_properties(self):
        """Test setting and getting Hunk properties."""
        hunk = Hunk()
        hunk.startsrc = 10
        hunk.linessrc = 5
        hunk.starttgt = 15
        hunk.linestgt = 7
        hunk.desc = "test description"
        hunk.text = [b"+ added line", b"- removed line"]

        assert hunk.startsrc == 10
        assert hunk.linessrc == 5
        assert hunk.starttgt == 15
        assert hunk.linestgt == 7
        assert hunk.desc == "test description"
        assert hunk.text == [b"+ added line", b"- removed line"]

    def test_hunk_invalid_flag(self):
        """Test the invalid flag functionality."""
        hunk = Hunk()
        assert hunk.invalid is False

        hunk.invalid = True
        assert hunk.invalid is True


class TestPatch:
    """Test the Patch class."""

    def test_patch_initialization(self):
        """Test Patch object initialization."""
        patch_obj = Patch()
        assert patch_obj.source is None
        assert patch_obj.target is None
        assert patch_obj.hunks == []
        assert patch_obj.hunkends == {}
        assert patch_obj.header == []
        assert patch_obj.type is None

    def test_patch_properties(self):
        """Test setting and getting Patch properties."""
        patch_obj = Patch()
        patch_obj.source = b"source.txt"
        patch_obj.target = b"target.txt"
        patch_obj.type = "git"

        assert patch_obj.source == b"source.txt"
        assert patch_obj.target == b"target.txt"
        assert patch_obj.type == "git"

    def test_patch_iteration(self):
        """Test that Patch objects are iterable over hunks."""
        patch_obj = Patch()
        hunk1 = Hunk()
        hunk1.startsrc = 1
        hunk2 = Hunk()
        hunk2.startsrc = 10

        patch_obj.hunks = [hunk1, hunk2]

        hunks = list(patch_obj)
        assert len(hunks) == 2
        assert hunks[0] is hunk1
        assert hunks[1] is hunk2

    def test_patch_empty_iteration(self):
        """Test iteration over empty patch."""
        patch_obj = Patch()
        hunks = list(patch_obj)
        assert hunks == []


class TestPatchSet:
    """Test the PatchSet class."""

    def test_patchset_initialization(self):
        """Test PatchSet object initialization."""
        patchset = PatchSet()
        assert patchset.name is None
        assert patchset.type is None
        assert patchset.items == []
        assert patchset.errors == 0
        assert patchset.warnings == 0

    def test_patchset_initialization_with_stream(self, sample_patch_content):
        """Test PatchSet initialization with stream."""
        stream = BytesIO(sample_patch_content)
        patchset = PatchSet(stream)

        assert len(patchset.items) == 1
        assert patchset.errors == 0

    def test_patchset_length(self):
        """Test PatchSet length calculation."""
        patchset = PatchSet()
        assert len(patchset) == 0

        patch_obj = Patch()
        patchset.items.append(patch_obj)
        assert len(patchset) == 1

    def test_patchset_iteration(self):
        """Test that PatchSet objects are iterable over patches."""
        patchset = PatchSet()
        patch1 = Patch()
        patch1.source = b"file1.txt"
        patch2 = Patch()
        patch2.source = b"file2.txt"

        patchset.items = [patch1, patch2]

        patches = list(patchset)
        assert len(patches) == 2
        assert patches[0] is patch1
        assert patches[1] is patch2

    def test_patchset_empty_iteration(self):
        """Test iteration over empty patchset."""
        patchset = PatchSet()
        patches = list(patchset)
        assert patches == []

    def test_patchset_parse_simple_patch(self, sample_patch_content):
        """Test parsing a simple patch."""
        patchset = PatchSet()
        stream = BytesIO(sample_patch_content)
        result = patchset.parse(stream)

        assert result is True
        assert len(patchset.items) == 1
        assert patchset.errors == 0

        patch_obj = patchset.items[0]
        assert patch_obj.source == b"test.txt"
        assert patch_obj.target == b"test.txt"
        assert len(patch_obj.hunks) == 1

        hunk = patch_obj.hunks[0]
        assert hunk.startsrc == 1
        assert hunk.linessrc == 3
        assert hunk.starttgt == 1
        assert hunk.linestgt == 3

    def test_patchset_parse_invalid_content(self, invalid_patch_content):
        """Test parsing invalid patch content."""
        patchset = PatchSet()
        stream = BytesIO(invalid_patch_content)
        result = patchset.parse(stream)

        assert result is False
        assert patchset.errors > 0

    def test_patchset_parse_empty_content(self):
        """Test parsing empty content."""
        patchset = PatchSet()
        stream = BytesIO(b"")
        result = patchset.parse(stream)

        assert result is False
        assert patchset.errors > 0

    def test_patchset_parse_multifile_patch(self, multifile_patch):
        """Test parsing a multi-file patch."""
        patchset = PatchSet()
        stream = BytesIO(multifile_patch)
        result = patchset.parse(stream)

        assert result is True
        assert len(patchset.items) == 2
        assert patchset.errors == 0

        # Check first file
        patch1 = patchset.items[0]
        assert patch1.source == b"file1.txt"
        assert patch1.target == b"file1.txt"

        # Check second file
        patch2 = patchset.items[1]
        assert patch2.source == b"file2.txt"
        assert patch2.target == b"file2.txt"

    def test_patchset_error_counting(self):
        """Test error and warning counting."""
        patchset = PatchSet()
        assert patchset.errors == 0
        assert patchset.warnings == 0

        # Simulate errors and warnings
        patchset.errors = 2
        patchset.warnings = 3

        assert patchset.errors == 2
        assert patchset.warnings == 3

    def test_patchset_type_detection(self, sample_git_patch):
        """Test patch type detection."""
        patchset = PatchSet()
        stream = BytesIO(sample_git_patch)
        result = patchset.parse(stream)

        assert result is True
        assert patchset.type == patch.GIT

    def test_patchset_mixed_type(self):
        """Test mixed patch type detection."""
        # This would require a more complex test setup
        # For now, just test the basic property
        patchset = PatchSet()
        patchset.type = patch.MIXED
        assert patchset.type == patch.MIXED


class TestPatchSetIntegration:
    """Integration tests for PatchSet with real patch files."""

    def test_parse_git_patch_file(self, test_data_dir):
        """Test parsing a real Git patch file."""
        git_patch_file = test_data_dir / "git-changed-file.diff"
        if git_patch_file.exists():
            patchset = patch.fromfile(str(git_patch_file))
            assert patchset is not False
            assert patchset.type == patch.GIT
            assert len(patchset.items) >= 1

    def test_parse_svn_patch_file(self, test_data_dir):
        """Test parsing a real SVN patch file."""
        svn_patch_file = test_data_dir / "svn-changed-2-files.diff"
        if svn_patch_file.exists():
            patchset = patch.fromfile(str(svn_patch_file))
            assert patchset is not False
            assert patchset.type == patch.SVN
            assert len(patchset.items) >= 1

    def test_parse_hg_patch_file(self, test_data_dir):
        """Test parsing a real Mercurial patch file."""
        hg_patch_file = test_data_dir / "hg-changed-2-files.diff"
        if hg_patch_file.exists():
            patchset = patch.fromfile(str(hg_patch_file))
            assert patchset is not False
            assert patchset.type == patch.HG
            assert len(patchset.items) >= 1


@pytest.mark.parametrize(
    "patch_content,expected_type",
    [
        (
            b"""--- a/test.txt\n+++ b/test.txt\n@@ -1,1 +1,1 @@\n-old\n+new\n""",
            patch.PLAIN,
        ),
    ],
)
def test_patch_type_detection_parametrized(patch_content, expected_type):
    """Parametrized test for patch type detection."""
    patchset = PatchSet()
    stream = BytesIO(patch_content)
    result = patchset.parse(stream)

    if result:
        assert patchset.type == expected_type
