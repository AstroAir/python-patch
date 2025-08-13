# Command Line Interface

The Python Patch command-line interface provides a powerful and flexible way to apply patches from the terminal. This guide covers all available options and common usage patterns.

## Basic Syntax

```bash
patch [OPTIONS] PATCH_FILE
```

## Command Line Options

### Core Options

#### `PATCH_FILE`

The patch file to apply. Can be a local file path or `-` to read from stdin.

```bash
# Apply local patch file
patch changes.patch

# Read patch from stdin
cat changes.patch | patch -

# Apply patch from URL (using curl)
curl -s https://example.com/patch.diff | patch -
```

#### `--strip=N` / `-p N`

Remove N leading path components from file paths in the patch.

```bash
# Remove 1 path component (common for Git patches)
patch --strip=1 feature.patch
patch -p1 feature.patch

# Remove 2 path components
patch --strip=2 deep-path.patch
```

**When to use different strip levels:**

- `--strip=0` (default): Use exact paths from patch
- `--strip=1`: Remove first path component (e.g., `a/file.txt` → `file.txt`)
- `--strip=2`: Remove two components (e.g., `project/src/file.txt` → `file.txt`)

#### `--directory=DIR` / `-d DIR`

Change to directory before applying patches.

```bash
# Apply patches relative to specific directory
patch --directory=/home/user/project changes.patch

# Combine with strip option
patch -d /path/to/project -p1 feature.patch
```

### Preview and Safety Options

#### `--dry-run`

Show what would be done without actually applying changes.

```bash
# Preview changes
patch --dry-run changes.patch

# Combine with verbose output
patch --dry-run --verbose feature.patch
```

#### `--reverse` / `-R`

Apply patches in reverse (undo changes).

```bash
# Reverse a previously applied patch
patch --reverse changes.patch

# Reverse with strip level
patch --reverse --strip=1 feature.patch
```

#### `--backup`

Create backup files before modifying originals.

```bash
# Create .orig backup files
patch --backup changes.patch

# Files will be backed up as filename.orig
```

### Output and Verbosity Options

#### `--verbose` / `-v`

Show detailed information during patch application.

```bash
# Verbose output
patch --verbose changes.patch

# Shows:
# - Files being processed
# - Hunks being applied
# - Success/failure status
```

#### `--quiet` / `-q`

Suppress normal output (only show errors).

```bash
# Silent operation
patch --quiet changes.patch
```

#### `--stats`

Show diffstat summary after applying patches.

```bash
# Show statistics
patch --stats changes.patch

# Output example:
#  file1.py |  10 +++++-----
#  file2.py |   5 +++++
#  2 files changed, 12 insertions(+), 5 deletions(-)
```

### Advanced Options

#### `--fuzz=N`

Set the fuzz factor for inexact matches (default: 2).

```bash
# Allow more context line differences
patch --fuzz=3 old-patch.patch

# Strict matching (no fuzz)
patch --fuzz=0 exact-patch.patch
```

#### `--force`

Force application even when patches seem to fail.

```bash
# Force application (use with caution)
patch --force problematic.patch
```

!!! warning "Use --force Carefully"
    The `--force` option can lead to incorrect results. Always review changes after using this option.

## Usage Examples

### Basic Operations

```bash
# Apply a simple patch
patch simple-fix.patch

# Apply Git-style patch
patch --strip=1 git-commit.patch

# Preview before applying
patch --dry-run --verbose feature.patch
```

### Working with Different Sources

```bash
# Apply patch from URL
curl -s https://github.com/user/repo/commit/abc123.patch | patch -p1 -

# Apply multiple patches
for patch_file in patches/*.patch; do
    echo "Applying $patch_file..."
    patch -p1 "$patch_file"
done

# Apply patches with error handling
if patch --dry-run -p1 risky.patch; then
    patch -p1 risky.patch
    echo "Patch applied successfully"
else
    echo "Patch would fail - skipping"
fi
```

### Directory-Based Operations

```bash
# Apply patches to different project
patch -d /path/to/project -p1 external.patch

# Apply patches from different location
cd /tmp
patch -d /home/user/project -p1 /path/to/patches/fix.patch
```

### Backup and Recovery

```bash
# Create backups before applying
patch --backup -p1 important-changes.patch

# If something goes wrong, restore from backups
for backup in *.orig; do
    original="${backup%.orig}"
    mv "$backup" "$original"
done
```

## Exit Codes

The patch command returns different exit codes based on the result:

| Exit Code | Meaning |
|-----------|---------|
| 0 | Success - all patches applied |
| 1 | Partial success - some patches failed |
| 2 | Error - patch file not found or invalid |
| 3 | Permission error |

### Using Exit Codes in Scripts

```bash
#!/bin/bash

if patch -p1 feature.patch; then
    echo "Patch applied successfully"
    # Continue with build process
    make build
else
    echo "Patch failed with exit code $?"
    exit 1
fi
```

## Integration with Version Control

### Git Integration

```bash
# Apply Git format patches
git format-patch HEAD~3  # Create patches
patch -p1 0001-feature.patch

# Or use git apply directly
git apply feature.patch
```

### SVN Integration

```bash
# Create SVN patch
svn diff > changes.patch

# Apply SVN patch
patch changes.patch  # Usually no strip needed
```

### Mercurial Integration

```bash
# Export Mercurial patches
hg export -r tip > latest.patch

# Apply with appropriate strip level
patch -p1 latest.patch
```

## Troubleshooting

### Common Issues and Solutions

#### "Patch does not apply"

```bash
# Try different strip levels
for strip in 0 1 2 3; do
    if patch --dry-run -p$strip problem.patch; then
        echo "Use strip level: $strip"
        patch -p$strip problem.patch
        break
    fi
done
```

#### "File not found"

```bash
# Check current directory
pwd
ls -la

# Use directory option
patch -d /correct/path -p1 patch.diff

# Or change directory first
cd /correct/path
patch -p1 /path/to/patch.diff
```

#### "Hunk failed"

```bash
# Increase fuzz factor
patch --fuzz=3 -p1 old-patch.patch

# Check for whitespace issues
patch --ignore-whitespace -p1 whitespace-patch.patch
```

### Debugging Tips

```bash
# Maximum verbosity
patch --verbose --dry-run -p1 debug.patch

# Check patch format
file patch.diff
head -20 patch.diff

# Validate patch syntax
patch --dry-run /dev/null < patch.diff
```

## Best Practices

### 1. Always Test First

```bash
# Never apply patches directly to important code
patch --dry-run -p1 untested.patch
```

### 2. Use Appropriate Strip Levels

```bash
# Check patch paths first
head -10 patch.diff | grep "^[+-][+-][+-]"

# Common patterns:
# --- a/file.txt    → use -p1
# --- file.txt      → use -p0
# --- src/file.txt  → depends on your location
```

### 3. Create Backups for Important Changes

```bash
# Always backup when applying to production code
patch --backup -p1 production-fix.patch
```

### 4. Validate Results

```bash
# After applying patches
git diff  # If using Git
svn diff  # If using SVN

# Run tests
make test
```

### 5. Script Patch Application

```bash
#!/bin/bash
set -e  # Exit on any error

PATCH_DIR="patches"
STRIP_LEVEL=1

for patch_file in "$PATCH_DIR"/*.patch; do
    echo "Testing $patch_file..."
    if patch --dry-run -p$STRIP_LEVEL "$patch_file"; then
        echo "Applying $patch_file..."
        patch -p$STRIP_LEVEL "$patch_file"
        echo "✓ Applied successfully"
    else
        echo "✗ Failed to apply $patch_file"
        exit 1
    fi
done

echo "All patches applied successfully!"
```

## Next Steps

- Learn about the [Python API](api.md) for programmatic patch handling
- Explore [Advanced Usage](advanced.md) patterns
- Check out [Error Handling](error-handling.md) strategies
- See practical [Examples](../examples/basic.md)
