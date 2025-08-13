# API Reference

This section provides comprehensive documentation for the Python Patch API. The library is designed with simplicity in mind while providing powerful functionality for parsing and applying unified diff patches.

## Overview

Python Patch provides a clean, well-documented API with three main entry points and several core classes:

### Main API Functions

- **[`fromfile()`](api.md#patch.fromfile)** - Parse patches from files
- **[`fromstring()`](api.md#patch.fromstring)** - Parse patches from strings/bytes
- **[`fromurl()`](api.md#patch.fromurl)** - Download and parse patches from URLs

### Core Classes

- **[`PatchSet`](core.md#patch.PatchSet)** - Collection of patches with application methods
- **[`Patch`](core.md#patch.Patch)** - Individual file patch containing hunks
- **[`Hunk`](core.md#patch.Hunk)** - Single diff hunk within a patch

## Quick Reference

### Basic Usage Pattern

```python
import patch

# 1. Parse a patch
patchset = patch.fromfile('changes.patch')

# 2. Check for errors
if not patchset:
    print("Failed to parse patch")
    exit(1)

# 3. Inspect contents (optional)
print(f"Patches for {len(patchset)} files")
for p in patchset:
    print(f"  {p.target}: +{p.added} -{p.removed}")

# 4. Apply patches
success = patchset.apply(strip=1)
if success:
    print("All patches applied successfully")
```

### Error Handling Pattern

```python
import patch

try:
    patchset = patch.fromfile('changes.patch')
    if patchset and patchset.errors == 0:
        success = patchset.apply(strip=1)
        if not success:
            print("Some patches failed to apply")
    else:
        print(f"Parse errors: {patchset.errors if patchset else 'Unknown'}")
except FileNotFoundError:
    print("Patch file not found")
except PermissionError:
    print("Permission denied")
```

## API Design Principles

### 1. Simple Entry Points

The API provides three simple functions for the most common patch sources:

```python
# From file
patchset = patch.fromfile('patch.diff')

# From string/bytes
patchset = patch.fromstring(patch_content)

# From URL
patchset = patch.fromurl('https://example.com/patch.diff')
```

### 2. Consistent Return Values

All parsing functions return either:

- A `PatchSet` object on success
- `False` on parsing failure

This allows for simple boolean checks:

```python
patchset = patch.fromfile('patch.diff')
if patchset:
    # Success - proceed with patch
    patchset.apply()
else:
    # Failure - handle error
    print("Failed to parse patch")
```

### 3. Rich Object Model

The returned objects provide detailed information:

```python
patchset = patch.fromfile('changes.patch')

# PatchSet level
print(f"Type: {patchset.type}")  # git, svn, plain, etc.
print(f"Errors: {patchset.errors}")
print(f"Warnings: {patchset.warnings}")

# Patch level (per file)
for patch_obj in patchset:
    print(f"File: {patch_obj.target}")
    print(f"Hunks: {len(patch_obj.hunks)}")
    
    # Hunk level (per change block)
    for hunk in patch_obj:
        print(f"  Lines: {hunk.startsrc}-{hunk.startsrc + hunk.linessrc}")
```

### 4. Flexible Application

The `apply()` method supports various options:

```python
# Basic application
patchset.apply()

# With path stripping
patchset.apply(strip=1)

# To specific directory
patchset.apply(root='/path/to/project')

# Dry run (preview only)
patchset.apply(dry_run=True)

# Combined options
patchset.apply(strip=1, root='/project', dry_run=True)
```

## Type Hints and IDE Support

Python Patch includes comprehensive type hints for better IDE integration:

```python
from typing import Union
import patch

# Type hints help with autocompletion and error detection
patchset: Union[patch.PatchSet, bool] = patch.fromfile('patch.diff')

if isinstance(patchset, patch.PatchSet):
    # IDE knows patchset is a PatchSet here
    success: bool = patchset.apply(strip=1)
```

## Backward Compatibility

The API maintains backward compatibility with older versions while adding new features:

```python
# Legacy usage still works
import patch
ps = patch.PatchSet()
ps.parse(open('patch.diff', 'rb'))

# Modern usage is preferred
patchset = patch.fromfile('patch.diff')
```

## Constants and Enums

The library provides constants for patch types:

```python
import patch

# Patch type constants
print(patch.GIT)        # 'git'
print(patch.SVN)        # 'svn'
print(patch.PLAIN)      # 'plain'
print(patch.MIXED)      # 'mixed'

# Check patch type
patchset = patch.fromfile('changes.patch')
if patchset.type == patch.GIT:
    print("This is a Git-format patch")
```

## Module Structure

The API is organized into several modules:

- **`patch.api`** - Main entry point functions
- **`patch.core`** - Core classes (PatchSet, Patch, Hunk)
- **`patch.parser`** - Parsing logic and utilities
- **`patch.application`** - Patch application and diffstat
- **`patch.cli`** - Command-line interface
- **`patch.utils`** - Utility functions
- **`patch.compat`** - Compatibility helpers

## Next Steps

- Explore the [Core Module](core.md) for detailed class documentation
- Check the [API Module](api.md) for function specifications
- See [Examples](../examples/basic.md) for practical usage patterns
- Review [Error Handling](../user-guide/error-handling.md) best practices
