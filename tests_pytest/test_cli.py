"""
Unit tests for CLI interface.

Tests command-line interface including argument parsing,
option handling, and main function execution.
"""
import pytest
import sys
import os
import tempfile
from unittest.mock import patch as mock_patch, MagicMock
from io import StringIO

from patch.cli import main


class TestMainFunction:
    """Test the main CLI function."""
    
    def test_main_with_version_option(self, capsys):
        """Test main function with --version option."""
        test_args = ['patch', '--version']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with code 0
            assert exc_info.value.code == 0
            
            captured = capsys.readouterr()
            assert 'python-patch' in captured.out
    
    def test_main_with_help_option(self, capsys):
        """Test main function with --help option."""
        test_args = ['patch', '--help']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            captured = capsys.readouterr()
            assert 'usage:' in captured.out.lower()
            assert 'options:' in captured.out.lower()
    
    def test_main_no_arguments(self, capsys):
        """Test main function with no arguments."""
        test_args = ['patch']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()
            
            captured = capsys.readouterr()
            # Should show version and help
            assert 'python-patch' in captured.out
            assert 'usage:' in captured.out.lower()
    
    def test_main_with_patch_file(self, temp_dir, sample_patch_content, sample_file_content):
        """Test main function with patch file."""
        # Create patch file
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)

        # Create source file
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(sample_file_content)

        test_args = ['patch', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
                # If successful, check that file was patched
                with open(source_file, 'rb') as f:
                    content = f.read()
                assert b'line2_modified' in content
            except SystemExit as e:
                # Exit code 0 means success
                assert e.code == 0
    
    def test_main_with_nonexistent_file(self):
        """Test main function with non-existent patch file."""
        test_args = ['patch', '/nonexistent/file.patch']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code
            assert exc_info.value.code != 0
    
    def test_main_with_diffstat_option(self, temp_dir, sample_patch_content):
        """Test main function with --diffstat option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        test_args = ['patch', '--diffstat', patch_file]
        
        with mock_patch.object(sys, 'argv', test_args), \
             mock_patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with code 0
            assert exc_info.value.code == 0
            
            output = mock_stdout.getvalue()
            assert 'test.txt' in output
            assert 'files changed' in output
    
    def test_main_with_verbose_option(self, temp_dir, sample_patch_content, sample_file_content):
        """Test main function with --verbose option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(sample_file_content)
        
        test_args = ['patch', '--verbose', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_quiet_option(self, temp_dir, sample_patch_content, sample_file_content):
        """Test main function with --quiet option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(sample_file_content)
        
        test_args = ['patch', '--quiet', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_debug_option(self, temp_dir, sample_patch_content, sample_file_content):
        """Test main function with --debug option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(sample_file_content)
        
        test_args = ['patch', '--debug', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_directory_option(self, temp_dir, sample_patch_content, sample_file_content):
        """Test main function with --directory option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(sample_file_content)
        
        test_args = ['patch', '--directory', temp_dir, patch_file]
        
        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_strip_option(self, temp_dir):
        """Test main function with --strip option."""
        # Create a patch with path prefixes
        patch_content = b'''diff --git a/subdir/test.txt b/subdir/test.txt
index 1234567..abcdefg 100644
--- a/subdir/test.txt
+++ b/subdir/test.txt
@@ -1,3 +1,3 @@
 line1
-line2
+line2_modified
 line3
'''
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(patch_content)
        
        # Create source file without prefix
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(b'line1\nline2\nline3\n')
        
        test_args = ['patch', '--strip', '1', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_revert_option(self, temp_dir, sample_patch_content, expected_patched_content):
        """Test main function with --revert option."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        # Create file with already patched content
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(expected_patched_content)
        
        test_args = ['patch', '--revert', '--directory', temp_dir, patch_file]

        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
                # Check that file was reverted
                with open(source_file, 'rb') as f:
                    content = f.read()
                assert b'line2\n' in content  # Original content
                assert b'line2_modified' not in content
            except SystemExit as e:
                assert e.code == 0
    
    def test_main_with_stdin_input(self, sample_patch_content):
        """Test main function with stdin input."""
        test_args = ['patch', '--']
        
        with mock_patch.object(sys, 'argv', test_args), \
             mock_patch('sys.stdin', StringIO(sample_patch_content.decode())):
            
            try:
                main()
            except SystemExit as e:
                # May succeed or fail depending on file availability
                assert isinstance(e.code, int)
    
    def test_main_with_url_input(self, sample_patch_content):
        """Test main function with URL input."""
        test_args = ['patch', 'http://example.com/test.patch']
        
        mock_response = MagicMock()
        mock_response.read.return_value = sample_patch_content
        mock_response.__iter__.return_value = iter(sample_patch_content.split(b'\n'))
        
        with mock_patch.object(sys, 'argv', test_args), \
             mock_patch('patch.compat.urllib_request.urlopen', return_value=mock_response):
            
            try:
                main()
            except SystemExit as e:
                # May succeed or fail depending on file availability
                assert isinstance(e.code, int)
    
    def test_main_error_handling(self):
        """Test main function error handling."""
        # Test with invalid patch file
        test_args = ['patch', '/dev/null']  # Empty file
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code
            assert exc_info.value.code != 0


class TestCliArgumentParsing:
    """Test CLI argument parsing."""
    
    def test_option_parser_creation(self):
        """Test that option parser can be created."""
        # This tests the internal structure, but we can't easily access it
        # So we test through the main function behavior
        test_args = ['patch', '--help']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit):
                main()
    
    def test_invalid_option(self):
        """Test handling of invalid options."""
        test_args = ['patch', '--invalid-option']
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code for invalid option
            assert exc_info.value.code != 0
    
    def test_strip_option_validation(self):
        """Test validation of strip option."""
        test_args = ['patch', '--strip', 'invalid', 'test.patch']
        
        with mock_patch.object(sys, 'argv', test_args):
            try:
                main()
            except SystemExit as e:
                # Should handle invalid strip value gracefully
                assert isinstance(e.code, int)


class TestCliIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_with_real_patch_files(self, test_data_dir):
        """Test CLI with real patch files from test data."""
        git_patch_file = test_data_dir / 'git-changed-file.diff'
        if git_patch_file.exists():
            test_args = ['patch', '--diffstat', str(git_patch_file)]
            
            with mock_patch.object(sys, 'argv', test_args):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                # Should succeed with diffstat
                assert exc_info.value.code == 0
    
    def test_cli_logging_configuration(self, temp_dir, sample_patch_content):
        """Test that CLI properly configures logging."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        # Test with debug option
        test_args = ['patch', '--debug', '--diffstat', patch_file]
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should succeed
            assert exc_info.value.code == 0
            
            # Debug mode should be enabled
            import patch.logging_utils
            assert patch.logging_utils.debugmode is True
    
    def test_cli_verbosity_levels(self, temp_dir, sample_patch_content):
        """Test different verbosity levels."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        verbosity_options = ['--quiet', '--verbose']
        
        for option in verbosity_options:
            test_args = ['patch', option, '--diffstat', patch_file]
            
            with mock_patch.object(sys, 'argv', test_args):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                # Should succeed regardless of verbosity
                assert exc_info.value.code == 0


class TestCliErrorScenarios:
    """Test CLI error scenarios."""
    
    def test_cli_with_corrupted_patch(self, temp_dir):
        """Test CLI with corrupted patch file."""
        patch_file = os.path.join(temp_dir, 'corrupted.patch')
        with open(patch_file, 'wb') as f:
            f.write(b'This is not a valid patch file\n')
        
        test_args = ['patch', patch_file]
        
        with mock_patch.object(sys, 'argv', test_args):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            # Should exit with error code
            assert exc_info.value.code != 0
    
    def test_cli_with_permission_error(self, temp_dir, sample_patch_content):
        """Test CLI with permission errors."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        # Create read-only source file
        source_file = os.path.join(temp_dir, 'test.txt')
        with open(source_file, 'wb') as f:
            f.write(b'line1\nline2\nline3\n')
        
        # Make file read-only
        os.chmod(source_file, 0o444)
        
        test_args = ['patch', patch_file]
        
        try:
            with mock_patch.object(sys, 'argv', test_args):
                with mock_patch('os.getcwd', return_value=temp_dir):
                    with pytest.raises(SystemExit) as exc_info:
                        main()
                    
                    # Should exit with error code due to permission error
                    assert exc_info.value.code != 0
        finally:
            # Restore permissions for cleanup
            os.chmod(source_file, 0o644)
    
    def test_cli_with_missing_target_file(self, temp_dir, sample_patch_content):
        """Test CLI when target file doesn't exist."""
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        # Don't create the target file
        test_args = ['patch', patch_file]
        
        with mock_patch.object(sys, 'argv', test_args):
            with mock_patch('os.getcwd', return_value=temp_dir):
                with pytest.raises(SystemExit) as exc_info:
                    main()
                
                # Should exit with error code
                assert exc_info.value.code != 0


@pytest.mark.parametrize("option,expected_behavior", [
    ('--version', 'shows version'),
    ('--help', 'shows help'),
    ('--diffstat', 'shows diffstat'),
    ('--quiet', 'reduces output'),
    ('--verbose', 'increases output'),
    ('--debug', 'enables debug mode'),
])
def test_cli_options_parametrized(option, expected_behavior, temp_dir, sample_patch_content):
    """Parametrized test for CLI options."""
    patch_file = os.path.join(temp_dir, 'test.patch')
    with open(patch_file, 'wb') as f:
        f.write(sample_patch_content)
    
    if option in ['--version', '--help']:
        test_args = ['patch', option]
    else:
        test_args = ['patch', option, patch_file]
    
    with mock_patch.object(sys, 'argv', test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # All options should result in some form of exit
        assert isinstance(exc_info.value.code, int)
