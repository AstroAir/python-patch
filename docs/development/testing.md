# Testing

This guide covers the testing strategy, frameworks, and best practices for Python Patch development.

## Testing Framework

Python Patch uses **pytest** as the primary testing framework, with legacy tests maintained for compatibility.

### Test Structure

```
tests_pytest/           # Modern pytest-based tests
├── conftest.py        # Pytest configuration and fixtures
├── test_api.py        # API function tests
├── test_core.py       # Core class tests
├── test_parser.py     # Parser functionality tests
├── test_application.py # Application logic tests
├── test_cli.py        # Command-line interface tests
├── test_utils.py      # Utility function tests
├── test_compat.py     # Compatibility layer tests
└── test_integration.py # Integration tests

tests/                  # Legacy test suite
├── run_tests.py       # Legacy test runner
├── data/              # Test data files
└── *.patch           # Sample patch files
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
python -m pytest tests_pytest/

# Run with verbose output
python -m pytest tests_pytest/ -v

# Run specific test file
python -m pytest tests_pytest/test_core.py

# Run specific test class
python -m pytest tests_pytest/test_core.py::TestPatchSet

# Run specific test method
python -m pytest tests_pytest/test_core.py::TestPatchSet::test_apply
```

### Coverage Testing

```bash
# Run tests with coverage
python -m pytest tests_pytest/ --cov=src/patch

# Generate HTML coverage report
python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Parallel Testing

```bash
# Run tests in parallel (faster)
python -m pytest tests_pytest/ -n auto

# Run with specific number of workers
python -m pytest tests_pytest/ -n 4
```

### Test Filtering

```bash
# Run only fast tests
python -m pytest tests_pytest/ -m "not slow"

# Run only integration tests
python -m pytest tests_pytest/ -m integration

# Run tests matching pattern
python -m pytest tests_pytest/ -k "test_apply"

# Skip specific tests
python -m pytest tests_pytest/ -k "not test_slow_operation"
```

## Writing Tests

### Test Fixtures

```python
# conftest.py
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def sample_patch_content():
    """Provide sample patch content for testing."""
    return b'''--- a/test.txt
+++ b/test.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
'''

@pytest.fixture
def sample_file_content():
    """Provide sample file content for patching."""
    return b"line1\nold line\nline3\n"

@pytest.fixture
def expected_patched_content():
    """Expected content after patch application."""
    return b"line1\nnew line\nline3\n"

@pytest.fixture
def complex_patchset():
    """Create a complex patchset for testing."""
    import patch
    
    patch_content = b'''--- a/file1.txt
+++ b/file1.txt
@@ -1,2 +1,3 @@
 existing line
+new line
 another line
--- a/file2.txt
+++ b/file2.txt
@@ -1,3 +1,2 @@
 keep this
-remove this
 keep this too
'''
    
    return patch.fromstring(patch_content)
```

### Test Categories

#### Unit Tests

```python
# test_core.py
import pytest
import patch
from patch.core import PatchSet, Patch, Hunk

class TestPatchSet:
    """Unit tests for PatchSet class."""
    
    def test_patchset_creation(self):
        """Test PatchSet initialization."""
        patchset = PatchSet()
        
        assert patchset.items == []
        assert patchset.errors == 0
        assert patchset.warnings == 0
        assert patchset.type is None
    
    def test_patchset_length(self, complex_patchset):
        """Test PatchSet length calculation."""
        assert len(complex_patchset) == 2
    
    def test_patchset_iteration(self, complex_patchset):
        """Test PatchSet iteration."""
        patches = list(complex_patchset)
        assert len(patches) == 2
        assert all(isinstance(p, Patch) for p in patches)
    
    def test_apply_success(self, temp_dir, sample_patch_content):
        """Test successful patch application."""
        # Create test file
        test_file = os.path.join(temp_dir, 'test.txt')
        with open(test_file, 'wb') as f:
            f.write(b"line1\nold line\nline3\n")
        
        # Parse and apply patch
        patchset = patch.fromstring(sample_patch_content)
        success = patchset.apply(root=temp_dir)
        
        assert success is True
        
        # Verify result
        with open(test_file, 'rb') as f:
            content = f.read()
        
        assert b"new line" in content
        assert b"old line" not in content
```

#### Integration Tests

```python
# test_integration.py
import pytest
import patch
import subprocess
import os

class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_cli_patch_application(self, temp_dir, sample_patch_content):
        """Test patch application via CLI."""
        
        # Create patch file
        patch_file = os.path.join(temp_dir, 'test.patch')
        with open(patch_file, 'wb') as f:
            f.write(sample_patch_content)
        
        # Create target file
        target_file = os.path.join(temp_dir, 'test.txt')
        with open(target_file, 'wb') as f:
            f.write(b"line1\nold line\nline3\n")
        
        # Run CLI command
        result = subprocess.run([
            'python', '-m', 'patch', patch_file
        ], cwd=temp_dir, capture_output=True, text=True)
        
        assert result.returncode == 0
        
        # Verify changes
        with open(target_file, 'rb') as f:
            content = f.read()
        
        assert b"new line" in content

@pytest.mark.slow
class TestPerformanceIntegration:
    """Performance integration tests."""
    
    def test_large_patch_performance(self, temp_dir):
        """Test performance with large patches."""
        
        # Create large patch content
        lines = []
        for i in range(1000):
            lines.append(f"--- a/file{i}.txt")
            lines.append(f"+++ b/file{i}.txt")
            lines.append("@@ -1,1 +1,1 @@")
            lines.append(f"-old content {i}")
            lines.append(f"+new content {i}")
        
        large_patch = '\n'.join(lines).encode('utf-8')
        
        # Create corresponding files
        for i in range(1000):
            file_path = os.path.join(temp_dir, f'file{i}.txt')
            with open(file_path, 'w') as f:
                f.write(f"old content {i}\n")
        
        # Test parsing and application
        import time
        start_time = time.time()
        
        patchset = patch.fromstring(large_patch)
        assert patchset is not False
        
        success = patchset.apply(root=temp_dir)
        assert success is True
        
        duration = time.time() - start_time
        
        # Performance assertion (adjust based on requirements)
        assert duration < 10.0  # Should complete within 10 seconds
        
        print(f"Large patch test completed in {duration:.2f} seconds")
```

### Property-Based Testing

```python
# test_property_based.py
import pytest
from hypothesis import given, strategies as st
import patch
from io import BytesIO

# Property-based testing with Hypothesis
@given(st.text(min_size=1, max_size=100))
def test_patch_content_roundtrip(content):
    """Test that valid patch content can be parsed and applied."""
    
    # Skip if content contains problematic characters
    if '\x00' in content or not content.strip():
        return
    
    # Create simple patch format
    patch_content = f'''--- a/test.txt
+++ b/test.txt
@@ -1,1 +1,1 @@
-original
+{content}
'''.encode('utf-8')
    
    # Test parsing
    patchset = patch.fromstring(patch_content)
    
    # If parsing succeeds, basic properties should hold
    if patchset:
        assert len(patchset) >= 0
        assert patchset.errors >= 0
        assert patchset.warnings >= 0

@given(st.integers(min_value=0, max_value=10))
def test_strip_level_bounds(strip_level):
    """Test that strip levels are handled correctly."""
    
    patch_content = b'''--- a/very/deep/path/to/file.txt
+++ b/very/deep/path/to/file.txt
@@ -1,1 +1,1 @@
-old
+new
'''
    
    patchset = patch.fromstring(patch_content)
    if patchset:
        # Should not crash with any valid strip level
        try:
            patchset.apply(strip=strip_level, dry_run=True)
        except Exception:
            # Some strip levels may be invalid, but shouldn't crash
            pass
```

## Test Data Management

### Creating Test Data

```python
# scripts/generate_test_data.py
import os
import random
import string

def generate_test_patches(output_dir='test_data'):
    """Generate various test patches for comprehensive testing."""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Simple addition patch
    simple_add = '''--- a/simple.txt
+++ b/simple.txt
@@ -1,2 +1,3 @@
 line1
+added line
 line2
'''
    
    with open(os.path.join(output_dir, 'simple_add.patch'), 'w') as f:
        f.write(simple_add)
    
    # Complex multi-file patch
    multi_file = '''--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
--- a/file2.txt
+++ b/file2.txt
@@ -1,2 +1,3 @@
 content1
+added content
 content2
'''
    
    with open(os.path.join(output_dir, 'multi_file.patch'), 'w') as f:
        f.write(multi_file)
    
    # Generate random patches for stress testing
    for i in range(10):
        patch_content = generate_random_patch(f'random{i}.txt')
        with open(os.path.join(output_dir, f'random_{i}.patch'), 'w') as f:
            f.write(patch_content)

def generate_random_patch(filename):
    """Generate a random patch for testing."""
    
    # Random content
    old_lines = [''.join(random.choices(string.ascii_letters, k=20)) for _ in range(5)]
    new_lines = old_lines.copy()
    
    # Make random changes
    for _ in range(random.randint(1, 3)):
        idx = random.randint(0, len(new_lines) - 1)
        new_lines[idx] = ''.join(random.choices(string.ascii_letters, k=20))
    
    # Create patch format
    patch_lines = [f'--- a/{filename}', f'+++ b/{filename}', '@@ -1,5 +1,5 @@']
    
    for old, new in zip(old_lines, new_lines):
        if old == new:
            patch_lines.append(f' {old}')
        else:
            patch_lines.append(f'-{old}')
            patch_lines.append(f'+{new}')
    
    return '\n'.join(patch_lines)

if __name__ == '__main__':
    generate_test_patches()
    print("Test data generated in test_data/ directory")
```

### Test Data Validation

```python
# scripts/validate_test_data.py
import patch
import glob
import os

def validate_test_patches(test_dir='test_data'):
    """Validate all test patches can be parsed."""
    
    patch_files = glob.glob(os.path.join(test_dir, '*.patch'))
    
    valid_count = 0
    invalid_count = 0
    
    for patch_file in patch_files:
        print(f"Validating {patch_file}...")
        
        patchset = patch.fromfile(patch_file)
        
        if patchset:
            print(f"  ✓ Valid - {len(patchset)} patches, {patchset.errors} errors")
            valid_count += 1
        else:
            print(f"  ✗ Invalid - failed to parse")
            invalid_count += 1
    
    print(f"\nValidation complete: {valid_count} valid, {invalid_count} invalid")
    return invalid_count == 0

if __name__ == '__main__':
    validate_test_patches()
```

## Continuous Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python-version: [3.7, 3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        python -m pytest tests_pytest/ -v --cov=src/patch
    
    - name: Run legacy tests
      run: |
        python tests/run_tests.py
    
    - name: Upload coverage
      if: matrix.os == 'ubuntu-latest' && matrix.python-version == '3.9'
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Test Quality Metrics

```bash
# Generate test quality report
python -m pytest tests_pytest/ \
  --cov=src/patch \
  --cov-report=html \
  --cov-report=xml \
  --cov-fail-under=90 \
  --junitxml=test-results.xml
```

## Test Best Practices

### 1. Test Organization

```python
class TestPatchApplication:
    """Organize related tests in classes."""
    
    def test_successful_application(self):
        """Test the happy path."""
        pass
    
    def test_application_failure(self):
        """Test failure scenarios."""
        pass
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        pass
```

### 2. Descriptive Test Names

```python
def test_patch_applies_successfully_with_strip_level_1():
    """Test names should describe what is being tested."""
    pass

def test_parser_handles_git_format_with_binary_files():
    """Include context about the specific scenario."""
    pass

def test_application_fails_gracefully_when_target_file_missing():
    """Describe both the condition and expected outcome."""
    pass
```

### 3. Test Data Management

```python
# Use fixtures for reusable test data
@pytest.fixture
def git_patch_with_renames():
    """Git patch that includes file renames."""
    return b'''diff --git a/old_name.txt b/new_name.txt
similarity index 100%
rename from old_name.txt
rename to new_name.txt
'''

@pytest.fixture
def svn_patch_with_properties():
    """SVN patch with property changes."""
    return b'''Index: file.txt
===================================================================
--- file.txt	(revision 123)
+++ file.txt	(working copy)
@@ -1,1 +1,1 @@
-old content
+new content

Property changes on: file.txt
___________________________________________________________________
Added: svn:executable
   + *
'''
```

### 4. Error Testing

```python
def test_parser_handles_malformed_patch():
    """Test parser error handling."""
    
    malformed_patch = b"This is not a valid patch"
    
    patchset = patch.fromstring(malformed_patch)
    assert patchset is False

def test_application_handles_missing_file():
    """Test application error handling."""
    
    patch_content = b'''--- a/nonexistent.txt
+++ b/nonexistent.txt
@@ -1,1 +1,1 @@
-old
+new
'''
    
    patchset = patch.fromstring(patch_content)
    assert patchset is not False
    
    # Should fail gracefully
    success = patchset.apply()
    assert success is False
```

## Performance Testing

### Benchmark Tests

```python
# test_performance.py
import pytest
import patch
import time
import os

@pytest.mark.slow
class TestPerformance:
    """Performance benchmark tests."""
    
    def test_large_patch_parsing_performance(self):
        """Test parsing performance with large patches."""
        
        # Generate large patch content
        lines = []
        for i in range(1000):
            lines.extend([
                f"--- a/file{i}.txt",
                f"+++ b/file{i}.txt", 
                "@@ -1,1 +1,1 @@",
                f"-old content {i}",
                f"+new content {i}"
            ])
        
        large_patch = '\n'.join(lines).encode('utf-8')
        
        # Measure parsing time
        start_time = time.time()
        patchset = patch.fromstring(large_patch)
        parse_time = time.time() - start_time
        
        assert patchset is not False
        assert len(patchset) == 1000
        assert parse_time < 5.0  # Should parse within 5 seconds
        
        print(f"Parsed 1000 patches in {parse_time:.3f} seconds")
    
    @pytest.mark.parametrize("file_count", [10, 100, 500])
    def test_application_scaling(self, temp_dir, file_count):
        """Test application performance scaling."""
        
        # Create test files and patch
        patch_lines = []
        
        for i in range(file_count):
            # Create test file
            test_file = os.path.join(temp_dir, f'file{i}.txt')
            with open(test_file, 'w') as f:
                f.write(f"original content {i}\n")
            
            # Add to patch
            patch_lines.extend([
                f"--- a/file{i}.txt",
                f"+++ b/file{i}.txt",
                "@@ -1,1 +1,1 @@",
                f"-original content {i}",
                f"+modified content {i}"
            ])
        
        patch_content = '\n'.join(patch_lines).encode('utf-8')
        
        # Measure application time
        patchset = patch.fromstring(patch_content)
        assert patchset is not False
        
        start_time = time.time()
        success = patchset.apply(root=temp_dir)
        apply_time = time.time() - start_time
        
        assert success is True
        
        # Performance should scale reasonably
        max_time = file_count * 0.01  # 10ms per file max
        assert apply_time < max_time
        
        print(f"Applied {file_count} patches in {apply_time:.3f} seconds")
```

## Test Automation

### Automated Test Discovery

```python
# scripts/run_all_tests.py
import subprocess
import sys
import os

def run_test_suite():
    """Run complete test suite with reporting."""
    
    print("Running Python Patch Test Suite")
    print("=" * 50)
    
    # Run pytest tests
    print("\n1. Running pytest tests...")
    pytest_result = subprocess.run([
        'python', '-m', 'pytest', 'tests_pytest/', 
        '-v', '--cov=src/patch', '--cov-report=term-missing'
    ])
    
    # Run legacy tests
    print("\n2. Running legacy tests...")
    legacy_result = subprocess.run([
        'python', 'tests/run_tests.py'
    ])
    
    # Run code quality checks
    print("\n3. Running code quality checks...")
    quality_checks = [
        (['black', '--check', 'src/', 'tests_pytest/'], "Black formatting"),
        (['isort', '--check-only', 'src/', 'tests_pytest/'], "Import sorting"),
        (['flake8', 'src/', 'tests_pytest/'], "Code style"),
        (['mypy', 'src/'], "Type checking")
    ]
    
    quality_results = []
    for command, description in quality_checks:
        print(f"  Running {description}...")
        result = subprocess.run(command, capture_output=True)
        quality_results.append((description, result.returncode == 0))
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUITE SUMMARY")
    print("=" * 50)
    
    pytest_success = pytest_result.returncode == 0
    legacy_success = legacy_result.returncode == 0
    quality_success = all(success for _, success in quality_results)
    
    print(f"Pytest tests: {'PASS' if pytest_success else 'FAIL'}")
    print(f"Legacy tests: {'PASS' if legacy_success else 'FAIL'}")
    
    for description, success in quality_results:
        print(f"{description}: {'PASS' if success else 'FAIL'}")
    
    overall_success = pytest_success and legacy_success and quality_success
    print(f"\nOverall: {'PASS' if overall_success else 'FAIL'}")
    
    return 0 if overall_success else 1

if __name__ == '__main__':
    sys.exit(run_test_suite())
```

## Next Steps

- Review [Development Setup](setup.md) for environment configuration
- Learn about [Contributing](contributing.md) guidelines
- Understand [Release Process](release.md) for maintainers
- Explore [API Reference](../api/index.md) for implementation details
