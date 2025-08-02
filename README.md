# Python Patch

A modern, robust Python library for parsing and applying unified diffs with comprehensive format support and automatic error correction.

[![CI](https://github.com/AstroAir/python-patch/actions/workflows/ci.yml/badge.svg)](https://github.com/AstroAir/python-patch/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/patch)](https://pypi.python.org/pypi/patch)
[![Python Versions](https://img.shields.io/pypi/pyversions/patch)](https://pypi.python.org/pypi/patch)
[![License](https://img.shields.io/pypi/l/patch)](https://github.com/AstroAir/python-patch/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/patch)](https://pypi.python.org/pypi/patch)

## Overview

Python Patch is a comprehensive library for working with unified diff files. It provides both a command-line interface and a Python API for parsing, analyzing, and applying patches from various version control systems.

## ✨ Key Features

### 🔧 **Robust Parsing & Application**

- **Multi-format support**: Git, Mercurial (HG), Subversion (SVN) patch formats
- **Automatic error correction**: Handles broken diffs, line ending issues, and path prefix problems
- **Smart detection**: Automatically identifies patch format and applies appropriate parsing rules

### 🛠️ **Developer-Friendly API**

- **Simple API**: Easy-to-use functions for common operations
- **Type hints**: Full type annotation support for better IDE integration
- **Comprehensive error handling**: Detailed error reporting and recovery options

### 🎯 **Production Ready**

- **Zero dependencies**: Uses only Python standard library
- **Cross-platform**: Works on Linux, Windows, and macOS
- **High test coverage**: Extensively tested with real-world patch files
- **Performance optimized**: Efficient parsing and memory usage

### 📊 **Rich Output**

- **Detailed diffstat**: Visual histogram showing changes per file
- **Progress reporting**: Track application progress for large patch sets
- **Flexible output formats**: JSON, plain text, and structured data

## ⚠️ Current Limitations

The following features are not yet supported:

- File renaming, creation, and removal operations
- Directory tree operations (mkdir, rmdir)
- Version control specific properties and metadata
- Non-unified diff formats (context diffs, ed scripts)

## 🚀 Quick Start

### Installation

Install from PyPI using pip:

```bash
# Install the latest stable version
pip install patch

# Install with development dependencies
pip install "patch[dev]"

# Install specific version (recommended for production)
pip install "patch==1.*"
```

### Command Line Usage

```bash
# Apply a patch file
patch diff.patch

# Apply with custom strip level
patch --strip=1 changes.patch

# Dry run (show what would be changed)
patch --dry-run feature.patch

# Reverse a patch
patch --reverse bugfix.patch

# Show detailed statistics
patch --verbose --stats updates.patch
```

### Python API Usage

#### Basic Operations

```python
import patch

# Parse and apply a patch file
patchset = patch.fromfile('changes.patch')
if patchset:
    success = patchset.apply(strip=1)
    print(f"Applied {len(patchset)} patches successfully: {success}")

# Parse patch from string
patch_content = """--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3"""

patchset = patch.fromstring(patch_content)
if patchset:
    patchset.apply()

# Download and apply patch from URL
patchset = patch.fromurl('https://github.com/user/repo/commit/abc123.patch')
if patchset:
    patchset.apply(strip=1)
```

#### Advanced Usage

```python
import patch

# Load patch with error handling
try:
    patchset = patch.fromfile('complex.patch')
    if not patchset:
        print("Failed to parse patch")
        exit(1)

    # Inspect patches before applying
    for p in patchset:
        print(f"File: {p.target}")
        print(f"Hunks: {len(p.hunks)}")
        print(f"Additions: +{p.added}, Deletions: -{p.removed}")

    # Apply with options
    success = patchset.apply(
        strip=1,           # Strip path components
        root='/path/to/project',  # Apply relative to directory
        dry_run=True       # Test without making changes
    )

    if success:
        print("All patches applied successfully!")
    else:
        print("Some patches failed to apply")

except FileNotFoundError:
    print("Patch file not found")
except PermissionError:
    print("Permission denied reading patch file")
```

## 📚 API Reference

### Core Functions

- **`patch.fromfile(filename)`** - Parse patch from file
- **`patch.fromstring(content)`** - Parse patch from string/bytes
- **`patch.fromurl(url)`** - Download and parse patch from URL

### PatchSet Methods

- **`apply(strip=0, root=None, dry_run=False)`** - Apply all patches
- **`revert()`** - Reverse all patches
- **`findfile(filename)`** - Find patch for specific file
- **`diffstat()`** - Generate diffstat summary

## 🧪 Testing

Run the test suite to ensure everything works correctly:

```bash
# Run modern pytest tests
python -m pytest tests_pytest/ -v

# Run with coverage report
python -m pytest tests_pytest/ --cov=src/patch --cov-report=html

# Run legacy test suite
python tests/run_tests.py

# Run specific test categories
python -m pytest tests_pytest/test_api.py -v
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/AstroAir/python-patch.git
cd python-patch

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest tests_pytest/
```

### Code Quality

We maintain high code quality standards:

```bash
# Format code
black src/ tests_pytest/

# Lint code
flake8 src/ tests_pytest/

# Type checking
mypy src/
```

## 📋 Requirements

- **Python**: 3.10+ (see pyproject.toml for full compatibility)
- **Dependencies**: None (uses only Python standard library)
- **Platforms**: Linux, Windows, macOS

## 📖 Documentation

- **[API Documentation](doc/)** - Detailed API reference
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](doc/CHANGES.md)** - Version history and changes
- **[Examples](examples/)** - Usage examples and tutorials

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Credits

- **Original Author**: anatoly techtonik
- **Current Maintainer**: Max Qian (<astro_air@126.com>)
- **Contributors**: See [CREDITS](doc/CREDITS) for full list

## 🔗 Links

- **PyPI Package**: <https://pypi.org/project/patch/>
- **Source Code**: <https://github.com/AstroAir/python-patch>
- **Issue Tracker**: <https://github.com/AstroAir/python-patch/issues>
- **CI/CD**: <https://github.com/AstroAir/python-patch/actions>

---

**Made with ❤️ by the Python community**
