# Contributing to Python Patch

Thank you for your interest in contributing to Python Patch! This document provides comprehensive guidelines for contributors.

## 🤝 Code of Conduct

This project adheres to a Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## 🚀 Quick Start

1. **Fork** the repository on GitHub
2. **Clone** your fork locally
3. **Set up** the development environment
4. **Create** a new branch for your changes
5. **Make** your changes with tests
6. **Test** your changes thoroughly
7. **Submit** a pull request

## 🛠️ Development Setup

### Prerequisites

- **Python 3.10+** (we recommend using the latest stable version)
- **Git** for version control
- **Virtual environment** tool (venv, conda, or pipenv)

### Environment Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/python-patch.git
cd python-patch

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Verify installation
python -c "import patch; print(patch.__version__)"
```

### Development Dependencies

The `[dev]` extra includes:

- **pytest** - Modern testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **flake8** - Code linting
- **mypy** - Type checking
- **pre-commit** - Git hooks for code quality

## 📝 Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/add-new-parser` - New features
- `fix/handle-unicode-errors` - Bug fixes
- `docs/update-api-examples` - Documentation updates
- `refactor/simplify-core-logic` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Examples:

```
feat(api): add support for binary patches
fix(parser): handle malformed hunk headers
docs(readme): update installation instructions
test(core): add edge case tests for PatchSet
```

Types:

- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `test` - Test additions/modifications
- `refactor` - Code refactoring
- `style` - Code style changes
- `perf` - Performance improvements
- `ci` - CI/CD changes

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests_pytest/ -v

# Run with coverage
python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

# Run specific test file
python -m pytest tests_pytest/test_api.py -v

# Run tests matching pattern
python -m pytest tests_pytest/ -k "test_fromfile" -v

# Run legacy tests (for compatibility)
python tests/run_tests.py
```

### Writing Tests

#### Test Structure

```python
"""
Test module for new functionality.

Tests should be comprehensive and cover edge cases.
"""

import pytest
import patch
from patch.core import PatchSet


class TestNewFeature:
    """Test class for new feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality works as expected."""
        # Arrange
        patch_content = "..."
        
        # Act
        result = patch.fromstring(patch_content)
        
        # Assert
        assert result is not False
        assert len(result) == 1
    
    def test_edge_case(self):
        """Test edge case handling."""
        # Test edge cases, error conditions, etc.
        pass
    
    @pytest.mark.parametrize("input_data,expected", [
        ("input1", "expected1"),
        ("input2", "expected2"),
    ])
    def test_parametrized(self, input_data, expected):
        """Test with multiple inputs."""
        result = some_function(input_data)
        assert result == expected
```

#### Test Guidelines

1. **Comprehensive Coverage**: Aim for high test coverage
2. **Edge Cases**: Test boundary conditions and error cases
3. **Clear Names**: Use descriptive test method names
4. **Arrange-Act-Assert**: Structure tests clearly
5. **Isolated Tests**: Each test should be independent
6. **Fast Tests**: Keep tests fast and focused

### Test Data

Use the existing test data in `tests/data/` or create new test files:

```python
import tempfile
import os

def test_with_temp_file():
    """Test using temporary files."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.patch', delete=False) as f:
        f.write(patch_content)
        temp_path = f.name
    
    try:
        result = patch.fromfile(temp_path)
        assert result is not False
    finally:
        os.unlink(temp_path)
```

## 🎨 Code Style

### Formatting with Black

```bash
# Format all code
black src/ tests_pytest/

# Check formatting
black --check src/ tests_pytest/
```

### Linting with Flake8

```bash
# Lint code
flake8 src/ tests_pytest/

# Configuration in setup.cfg or pyproject.toml
```

### Type Checking with MyPy

```bash
# Type check
mypy src/

# Configuration in pyproject.toml
```

### Code Style Guidelines

1. **Follow PEP 8** - Python style guide
2. **Use Type Hints** - Add type annotations to new code
3. **Document Functions** - Use Google-style docstrings
4. **Keep Functions Small** - Single responsibility principle
5. **Use Descriptive Names** - Clear variable and function names

### Example Code Style

```python
from typing import Optional, Union, List
import os


def parse_patch_file(
    filename: str,
    encoding: str = "utf-8"
) -> Optional[PatchSet]:
    """Parse a patch file and return a PatchSet.
    
    Args:
        filename: Path to the patch file to parse.
        encoding: Character encoding to use for reading.
        
    Returns:
        PatchSet object if parsing succeeds, None if it fails.
        
    Raises:
        FileNotFoundError: If the file doesn't exist.
        PermissionError: If the file can't be read.
        
    Example:
        >>> patchset = parse_patch_file('changes.patch')
        >>> if patchset:
        ...     print(f"Loaded {len(patchset)} patches")
    """
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Patch file not found: {filename}")
    
    # Implementation here...
    return patchset
```

## 📚 Documentation

### Docstring Style

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int = 0) -> bool:
    """Brief description of the function.
    
    Longer description if needed. Explain the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1.
        param2: Description of param2. Defaults to 0.
        
    Returns:
        Description of return value.
        
    Raises:
        ValueError: When param1 is invalid.
        TypeError: When param2 is not an integer.
        
    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
        
    Note:
        Any additional notes or warnings.
    """
```

### Documentation Updates

When adding new features:

1. **Update API docs** - Add docstrings to new functions/classes
2. **Update user guide** - Add usage examples
3. **Update examples** - Provide practical examples
4. **Update changelog** - Document changes

### Building Documentation

```bash
# Install MkDocs and dependencies
pip install mkdocs mkdocs-material mkdocstrings

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## 🔄 Pull Request Process

### Before Submitting

1. **Run all tests** and ensure they pass
2. **Format code** with black
3. **Lint code** with flake8
4. **Type check** with mypy
5. **Update documentation** if needed
6. **Add tests** for new functionality
7. **Update changelog** if appropriate

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Documentation updated
- [ ] Changelog updated (if applicable)
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by maintainers
3. **Testing** on multiple platforms
4. **Documentation review** if applicable
5. **Approval** and merge

## 🐛 Reporting Issues

### Bug Reports

Include:

1. **Python version** and operating system
2. **Package version** of python-patch
3. **Minimal reproduction** example
4. **Expected behavior** vs actual behavior
5. **Error messages** and stack traces
6. **Patch file** that causes the issue (if applicable)

### Feature Requests

Include:

1. **Use case** description
2. **Proposed solution** or API
3. **Alternative solutions** considered
4. **Additional context** or examples

## 🏷️ Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release tag
5. Build and upload to PyPI
6. Update documentation
7. Create GitHub release

## 💬 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Email**: Contact maintainers directly for sensitive issues

## 🙏 Recognition

Contributors are recognized in:

- **CHANGELOG.md** - For significant contributions
- **README.md** - In the contributors section
- **GitHub contributors** - Automatic recognition

Thank you for contributing to Python Patch! 🎉
