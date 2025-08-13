# Installation

This guide will help you install Python Patch and get it running on your system.

## Requirements

Python Patch has minimal requirements:

- **Python**: 3.10 or higher
- **Dependencies**: None (uses only Python standard library)
- **Platforms**: Linux, Windows, macOS

!!! note "Python Version Support"
    While Python Patch supports Python 3.10+, we recommend using the latest stable Python version for the best experience and security updates.

## Installation Methods

### From PyPI (Recommended)

The easiest way to install Python Patch is from PyPI using pip:

```bash
# Install the latest stable version
pip install patch
```

#### Development Dependencies

If you plan to contribute to the project or run tests, install with development dependencies:

```bash
pip install "patch[dev]"
```

This includes additional packages for testing, linting, and development:

- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `flake8` - Code linting
- `mypy` - Type checking

#### Version Pinning

For production environments, it's recommended to pin to a specific version:

```bash
# Pin to major version (recommended)
pip install "patch==1.*"

# Pin to specific version
pip install "patch==1.0.0"
```

### From Source

You can also install directly from the source repository:

```bash
# Install from GitHub main branch
pip install git+https://github.com/AstroAir/python-patch.git

# Install from specific tag
pip install git+https://github.com/AstroAir/python-patch.git@v1.0.0
```

### Development Installation

For development work, clone the repository and install in editable mode:

```bash
# Clone the repository
git clone https://github.com/AstroAir/python-patch.git
cd python-patch

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

## Virtual Environment Setup

We strongly recommend using a virtual environment to avoid conflicts with other packages:

=== "venv (Built-in)"

    ```bash
    # Create virtual environment
    python -m venv patch-env
    
    # Activate (Linux/macOS)
    source patch-env/bin/activate
    
    # Activate (Windows)
    patch-env\Scripts\activate
    
    # Install patch
    pip install patch
    ```

=== "conda"

    ```bash
    # Create conda environment
    conda create -n patch-env python=3.11
    
    # Activate environment
    conda activate patch-env
    
    # Install patch
    pip install patch
    ```

=== "pipenv"

    ```bash
    # Create Pipfile and install
    pipenv install patch
    
    # Activate shell
    pipenv shell
    ```

## Verification

After installation, verify that Python Patch is working correctly:

### Command Line

```bash
# Check version
patch --version

# Show help
patch --help
```

### Python API

```python
import patch

# Check version
print(patch.__version__)

# Test basic functionality
patchset = patch.fromstring("""--- a/test.txt
+++ b/test.txt
@@ -1 +1 @@
-old
+new""")

print(f"Parsed {len(patchset)} patches")
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'patch'

This usually means the package isn't installed or you're not in the correct virtual environment.

**Solution:**

```bash
# Ensure you're in the correct environment
which python
pip list | grep patch

# Reinstall if necessary
pip install --force-reinstall patch
```

#### Permission Denied

On some systems, you might need elevated permissions.

**Solution:**

```bash
# Install for current user only
pip install --user patch

# Or use sudo (Linux/macOS)
sudo pip install patch
```

#### Version Conflicts

If you have multiple Python versions or conflicting packages:

**Solution:**

```bash
# Use specific Python version
python3.11 -m pip install patch

# Create clean virtual environment
python -m venv clean-env
source clean-env/bin/activate
pip install patch
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/AstroAir/python-patch/issues)
2. Search for existing solutions
3. Create a new issue with:
   - Your Python version (`python --version`)
   - Your operating system
   - Complete error message
   - Steps to reproduce

## Next Steps

Once you have Python Patch installed:

- Continue to [Quick Start](quick-start.md) for your first patch operations
- Read the [Basic Usage](basic-usage.md) guide for common patterns
- Explore the [User Guide](../user-guide/cli.md) for advanced features
