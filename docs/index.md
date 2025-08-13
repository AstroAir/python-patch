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

### Basic Usage

=== "Command Line"

    ```bash
    # Apply a patch file
    patch diff.patch
    
    # Apply with custom strip level
    patch --strip=1 changes.patch
    
    # Dry run (show what would be changed)
    patch --dry-run feature.patch
    
    # Reverse a patch
    patch --reverse bugfix.patch
    ```

=== "Python API"

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
    ```

## 📚 Documentation Structure

This documentation is organized into several sections:

- **[Getting Started](getting-started/installation.md)**: Installation, quick start, and basic usage
- **[User Guide](user-guide/cli.md)**: Comprehensive guides for CLI and API usage
- **[API Reference](api/index.md)**: Detailed API documentation
- **[Examples](examples/basic.md)**: Practical examples and use cases
- **[Development](development/contributing.md)**: Contributing guidelines and development setup

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](development/contributing.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [License](about/license.md) page for details.

## 🙏 Credits

- **Original Author**: anatoly techtonik
- **Current Maintainer**: Max Qian (<astro_air@126.com>)
- **Contributors**: See [Credits](about/credits.md) for full list

---

**Made with ❤️ by the Python community**
