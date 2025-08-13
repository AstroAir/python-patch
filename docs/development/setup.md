# Development Setup

This guide covers setting up a development environment for contributing to Python Patch, including all necessary tools, dependencies, and configuration.

## Prerequisites

### System Requirements

- **Python 3.7+** (Python 3.9+ recommended)
- **Git** for version control
- **Make** (optional, for convenience commands)

### Supported Platforms

- Linux (Ubuntu 18.04+, CentOS 7+, etc.)
- macOS (10.14+)
- Windows (10+, with WSL recommended)

## Environment Setup

### 1. Clone the Repository

```bash
# Clone the repository
git clone https://github.com/AstroAir/python-patch.git
cd python-patch

# Create a development branch
git checkout -b feature/your-feature-name
```

### 2. Python Environment

#### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Using conda

```bash
# Create conda environment
conda create -n python-patch python=3.9
conda activate python-patch

# Install pip in conda environment
conda install pip
```

### 3. Install Dependencies

#### Development Dependencies

```bash
# Install package in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt

# Or install with development extras
pip install -e ".[dev]"
```

#### Core Development Tools

```bash
# Testing framework
pip install pytest pytest-cov pytest-xdist

# Code quality tools
pip install black isort flake8 mypy

# Documentation tools
pip install mkdocs mkdocs-material mkdocstrings[python]

# Pre-commit hooks
pip install pre-commit
pre-commit install
```

### 4. Verify Installation

```bash
# Run basic tests
python -m pytest tests_pytest/ -v

# Check code style
black --check src/
flake8 src/

# Type checking
mypy src/

# Build documentation
mkdocs build
```

## Development Workflow

### 1. Code Style and Formatting

The project uses several tools to maintain code quality:

```bash
# Format code with Black
black src/ tests_pytest/

# Sort imports with isort
isort src/ tests_pytest/

# Check code style with flake8
flake8 src/ tests_pytest/

# Type checking with mypy
mypy src/
```

#### Configuration Files

The project includes configuration for all tools:

- **`.flake8`** - Flake8 configuration
- **`pyproject.toml`** - Black, isort, and other tool configuration
- **`mypy.ini`** - MyPy type checking configuration

### 2. Testing

#### Running Tests

```bash
# Run all tests
python -m pytest tests_pytest/

# Run with coverage
python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

# Run specific test file
python -m pytest tests_pytest/test_core.py -v

# Run tests in parallel
python -m pytest tests_pytest/ -n auto

# Run legacy tests
python tests/run_tests.py
```

#### Test Structure

```
tests_pytest/
├── conftest.py          # Pytest configuration and fixtures
├── test_api.py          # API function tests
├── test_core.py         # Core class tests
├── test_parser.py       # Parser functionality tests
├── test_application.py  # Application logic tests
├── test_cli.py          # Command-line interface tests
├── test_utils.py        # Utility function tests
└── test_integration.py  # Integration tests
```

#### Writing Tests

```python
# Example test structure
import pytest
import patch

class TestNewFeature:
    """Tests for new feature functionality."""
    
    def test_basic_functionality(self):
        """Test basic feature operation."""
        # Arrange
        patch_content = "..."
        
        # Act
        result = patch.fromstring(patch_content)
        
        # Assert
        assert result is not False
        assert len(result) == 1
    
    @pytest.mark.parametrize("input_data,expected", [
        ("test1", "result1"),
        ("test2", "result2"),
    ])
    def test_parametrized_feature(self, input_data, expected):
        """Test feature with multiple inputs."""
        result = your_function(input_data)
        assert result == expected
    
    def test_error_handling(self):
        """Test error conditions."""
        with pytest.raises(ValueError):
            invalid_operation()
```

### 3. Documentation

#### Building Documentation

```bash
# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve

# Build with strict mode (fail on warnings)
mkdocs build --strict

# Clean build
mkdocs build --clean
```

#### Documentation Structure

```
docs/
├── index.md              # Homepage
├── getting-started/      # Installation and basic usage
├── user-guide/          # Detailed usage guides
├── api/                 # API reference documentation
├── examples/            # Code examples
├── development/         # Development guides
└── about/               # Project information
```

#### Writing Documentation

- Use **Markdown** for all documentation
- Include **code examples** for all features
- Use **mkdocstrings** for API documentation
- Follow the existing **style and structure**

### 4. Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

#### Hook Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

## IDE Configuration

### Visual Studio Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests_pytest/"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. **Open project** in PyCharm
2. **Configure interpreter**: Settings → Project → Python Interpreter → Add → Existing environment → `venv/bin/python`
3. **Enable tools**: Settings → Tools → External Tools
4. **Configure pytest**: Settings → Tools → Python Integrated Tools → Testing → pytest

## Debugging

### Debug Configuration

```python
# debug_patch.py - Debug script template
import patch
import logging
import sys

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

def debug_patch_operation(patch_file):
    """Debug a specific patch operation."""
    
    print(f"Debugging patch: {patch_file}")
    
    # Parse with debug info
    patchset = patch.fromfile(patch_file)
    
    if not patchset:
        print("Failed to parse patch")
        return
    
    print(f"Parsed {len(patchset)} patches")
    print(f"Errors: {patchset.errors}")
    print(f"Warnings: {patchset.warnings}")
    print(f"Type: {patchset.type}")
    
    # Analyze each patch
    for i, patch_obj in enumerate(patchset):
        print(f"\nPatch {i+1}:")
        print(f"  Source: {patch_obj.source}")
        print(f"  Target: {patch_obj.target}")
        print(f"  Type: {patch_obj.type}")
        print(f"  Hunks: {len(patch_obj.hunks)}")
        print(f"  Changes: +{patch_obj.added} -{patch_obj.removed}")
        
        # Analyze hunks
        for j, hunk in enumerate(patch_obj.hunks):
            print(f"    Hunk {j+1}: lines {hunk.startsrc}-{hunk.startsrc + hunk.linessrc - 1}")
            print(f"      Invalid: {hunk.invalid}")
            print(f"      Description: {hunk.desc}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python debug_patch.py <patch_file>")
        sys.exit(1)
    
    debug_patch_operation(sys.argv[1])
```

### Common Debug Scenarios

```bash
# Debug parsing issues
python debug_patch.py problematic.patch

# Debug with Python debugger
python -m pdb debug_patch.py test.patch

# Debug specific test
python -m pytest tests_pytest/test_parser.py::test_specific_case -v -s --pdb
```

## Performance Profiling

### Basic Profiling

```python
# profile_patch.py
import cProfile
import pstats
import patch

def profile_patch_operation(patch_file):
    """Profile patch operation performance."""
    
    def operation():
        patchset = patch.fromfile(patch_file)
        if patchset:
            patchset.apply()
    
    # Run profiler
    profiler = cProfile.Profile()
    profiler.enable()
    
    operation()
    
    profiler.disable()
    
    # Analyze results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

# Usage
profile_patch_operation('large.patch')
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory-profiler

# Profile memory usage
python -m memory_profiler profile_patch.py
```

## Troubleshooting

### Common Development Issues

#### 1. Import Errors

```bash
# Ensure package is installed in development mode
pip install -e .

# Check Python path
python -c "import sys; print(sys.path)"

# Verify package installation
pip list | grep patch
```

#### 2. Test Failures

```bash
# Run tests with verbose output
python -m pytest tests_pytest/ -v -s

# Run specific failing test
python -m pytest tests_pytest/test_core.py::TestPatchSet::test_apply -v -s

# Check test dependencies
pip install -r requirements-dev.txt
```

#### 3. Documentation Build Issues

```bash
# Check MkDocs configuration
mkdocs build --verbose

# Install documentation dependencies
pip install mkdocs mkdocs-material mkdocstrings[python]

# Clear documentation cache
rm -rf site/
mkdocs build --clean
```

#### 4. Code Style Issues

```bash
# Fix formatting automatically
black src/ tests_pytest/
isort src/ tests_pytest/

# Check remaining issues
flake8 src/ tests_pytest/
mypy src/
```

## Development Tools

### Useful Scripts

Create `scripts/dev-setup.sh`:

```bash
#!/bin/bash
# Development setup script

set -e

echo "Setting up Python Patch development environment..."

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run initial tests
python -m pytest tests_pytest/ -v

# Build documentation
mkdocs build

echo "Development environment setup complete!"
echo "Activate with: source venv/bin/activate"
```

### Makefile (Optional)

```makefile
# Makefile for development tasks

.PHONY: install test lint format docs clean

install:
	pip install -e .
	pip install -r requirements-dev.txt

test:
	python -m pytest tests_pytest/ -v

test-cov:
	python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

lint:
	flake8 src/ tests_pytest/
	mypy src/

format:
	black src/ tests_pytest/
	isort src/ tests_pytest/

docs:
	mkdocs build

docs-serve:
	mkdocs serve

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf site/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

all: format lint test docs
```

## Next Steps

- Read [Contributing Guidelines](contributing.md) for contribution process
- Learn about [Testing](testing.md) practices and requirements
- Understand [Release Process](release.md) for maintainers
- Explore [API Reference](../api/index.md) for implementation details
