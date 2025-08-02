# Contributing to python-patch

Thank you for your interest in contributing to python-patch! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up the development environment
4. Create a new branch for your changes
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Setup

### Prerequisites

- Python 2.7 or Python 3.4+
- Git

### Setting up the development environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/python-patch.git
cd python-patch

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-parser` for new features
- `bugfix/fix-unicode-handling` for bug fixes
- `docs/update-readme` for documentation updates

### Commit Messages

Write clear, concise commit messages:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests_pytest/

# Run with coverage
python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

# Run legacy tests
python tests/run_tests.py
```

### Writing Tests

- Add tests for any new functionality
- Ensure all tests pass before submitting
- Aim for high test coverage
- Use descriptive test names
- Follow the existing test patterns

## Submitting Changes

### Pull Request Process

1. Ensure your code follows the coding standards
2. Update documentation as needed
3. Add or update tests for your changes
4. Ensure all tests pass
5. Update the CHANGELOG if applicable
6. Submit a pull request with a clear description

### Pull Request Description

Include:
- A clear description of the changes
- The motivation for the changes
- Any breaking changes
- Screenshots (if applicable)
- References to related issues

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and small
- Use type hints where appropriate (Python 3.5+)

### Code Formatting

We use automated code formatting:

```bash
# Format code with black
black src/ tests_pytest/

# Check with flake8
flake8 src/ tests_pytest/

# Type checking with mypy
mypy src/
```

### Compatibility

- Maintain compatibility with Python 2.7 and Python 3.4+
- Use `from __future__ import` statements for Python 2/3 compatibility
- Test on multiple Python versions when possible

## Documentation

### Docstrings

Use Google-style docstrings:

```python
def apply_patch(patch_content, target_file):
    """Apply a patch to a target file.
    
    Args:
        patch_content (str): The patch content to apply.
        target_file (str): Path to the target file.
        
    Returns:
        bool: True if patch was applied successfully, False otherwise.
        
    Raises:
        PatchError: If the patch cannot be applied.
    """
```

### README Updates

- Update README.md if you add new features
- Include usage examples for new functionality
- Keep the documentation clear and concise

## Questions?

If you have questions about contributing, please:
- Check existing issues and pull requests
- Create a new issue with the "question" label
- Reach out to the maintainers

Thank you for contributing to python-patch!
