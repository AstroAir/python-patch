# CLI Module

The `patch.cli` module provides the command-line interface for the Python Patch library. It offers a comprehensive set of options for applying patches from various sources with flexible configuration.

## Functions

::: patch.cli.main
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Command-Line Usage

### Basic Commands

```bash
# Apply a patch file
python -m patch changes.patch

# Apply with path stripping (remove N leading path components)
python -m patch -p1 changes.patch
python -m patch --strip=2 changes.patch

# Apply to specific directory
python -m patch -d /target/directory changes.patch
python -m patch --directory=/target/directory changes.patch
```

### Advanced Options

```bash
# Show diffstat only (don't apply)
python -m patch --diffstat changes.patch

# Reverse/revert a patch
python -m patch --revert changes.patch

# Verbose output
python -m patch -v changes.patch
python -m patch --verbose changes.patch

# Quiet mode (errors only)
python -m patch -q changes.patch
python -m patch --quiet changes.patch

# Debug mode
python -m patch --debug changes.patch
```

### Input Sources

```bash
# From local file
python -m patch local-changes.patch

# From URL
python -m patch https://github.com/user/repo/commit/abc123.patch

# From stdin
cat changes.patch | python -m patch --
curl -s https://example.com/patch.diff | python -m patch --
```

## Usage Examples

### Basic Patch Application

```bash
# Download and apply a GitHub commit patch
python -m patch https://github.com/torvalds/linux/commit/abc123.patch

# Apply with path stripping (common for GitHub patches)
python -m patch -p1 https://github.com/user/repo/commit/def456.patch

# Apply to different directory
python -m patch -d /opt/myproject -p1 feature.patch
```

### Inspection and Validation

```bash
# Show what changes would be made (dry run)
python -m patch --diffstat feature.patch

# Example output:
#  src/main.py    |  15 +++++++++------
#  tests/test.py  |   8 ++++++++
#  README.md      |   3 ++-
#  3 files changed, 19 insertions(+), 7 deletions(-)

# Verbose mode for detailed information
python -m patch -v --diffstat complex-changes.patch
```

### Error Handling and Debugging

```bash
# Debug mode for troubleshooting
python -m patch --debug problematic.patch

# Quiet mode for scripts (only show errors)
python -m patch -q automated-patch.patch

# Check exit code in scripts
python -m patch changes.patch
if [ $? -eq 0 ]; then
    echo "Patch applied successfully"
else
    echo "Patch application failed"
fi
```

### Batch Processing

```bash
# Apply multiple patches in sequence
for patch_file in patches/*.patch; do
    echo "Applying $patch_file..."
    python -m patch -p1 "$patch_file"
    
    if [ $? -ne 0 ]; then
        echo "Failed to apply $patch_file"
        break
    fi
done

# Apply patches from a list
while read -r patch_url; do
    python -m patch -p1 "$patch_url"
done < patch_urls.txt
```

## Integration Examples

### CI/CD Pipeline Integration

```bash
#!/bin/bash
# ci-apply-patches.sh

set -e  # Exit on any error

PATCH_DIR="patches"
TARGET_DIR="/workspace"
STRIP_LEVEL=1

echo "Applying patches from $PATCH_DIR to $TARGET_DIR"

# Validate all patches first
for patch_file in "$PATCH_DIR"/*.patch; do
    if [ -f "$patch_file" ]; then
        echo "Validating $(basename "$patch_file")..."
        python -m patch --diffstat "$patch_file" > /dev/null
        
        if [ $? -ne 0 ]; then
            echo "ERROR: Invalid patch file: $patch_file"
            exit 1
        fi
    fi
done

# Apply patches
for patch_file in "$PATCH_DIR"/*.patch; do
    if [ -f "$patch_file" ]; then
        echo "Applying $(basename "$patch_file")..."
        python -m patch -d "$TARGET_DIR" -p"$STRIP_LEVEL" "$patch_file"
        
        if [ $? -ne 0 ]; then
            echo "ERROR: Failed to apply $patch_file"
            exit 1
        fi
    fi
done

echo "All patches applied successfully"
```

### Docker Integration

```dockerfile
# Dockerfile example
FROM python:3.9-slim

# Install python-patch
RUN pip install python-patch

# Copy patches
COPY patches/ /patches/

# Apply patches during build
RUN for patch in /patches/*.patch; do \
        python -m patch -p1 "$patch"; \
    done

# Continue with application setup...
```

### Git Hook Integration

```bash
#!/bin/bash
# pre-commit hook example

# Check if any .patch files are being committed
patch_files=$(git diff --cached --name-only --diff-filter=A | grep '\.patch$')

if [ -n "$patch_files" ]; then
    echo "Validating patch files..."
    
    for patch_file in $patch_files; do
        echo "Checking $patch_file..."
        
        # Validate patch syntax
        python -m patch --diffstat "$patch_file" > /dev/null
        
        if [ $? -ne 0 ]; then
            echo "ERROR: Invalid patch file: $patch_file"
            echo "Please fix the patch before committing"
            exit 1
        fi
    done
    
    echo "All patch files validated successfully"
fi
```

## Exit Codes

The CLI returns specific exit codes for different scenarios:

- **0**: Success - all operations completed successfully
- **1**: General error - patch parsing or application failed
- **2**: File not found - specified patch file doesn't exist
- **3**: Permission error - insufficient permissions to read/write files
- **4**: Network error - failed to download patch from URL
- **5**: Invalid arguments - incorrect command-line options

### Exit Code Handling

```bash
# Handle different exit codes
python -m patch changes.patch
exit_code=$?

case $exit_code in
    0)
        echo "Patch applied successfully"
        ;;
    1)
        echo "Patch application failed"
        ;;
    2)
        echo "Patch file not found"
        ;;
    3)
        echo "Permission denied"
        ;;
    4)
        echo "Network error downloading patch"
        ;;
    5)
        echo "Invalid command-line arguments"
        ;;
    *)
        echo "Unknown error (exit code: $exit_code)"
        ;;
esac
```

## Configuration

### Environment Variables

The CLI respects several environment variables:

```bash
# Set default strip level
export PATCH_STRIP=1
python -m patch changes.patch  # Uses strip=1 by default

# Set default target directory
export PATCH_ROOT=/project
python -m patch changes.patch  # Applies to /project

# Enable debug mode
export PATCH_DEBUG=1
python -m patch changes.patch  # Runs in debug mode
```

### Configuration File

Create a `.patchrc` file for default settings:

```ini
# .patchrc
[defaults]
strip = 1
verbose = true
backup = true

[paths]
patch_dir = patches/
target_dir = /workspace
```

## Troubleshooting

### Common Issues

1. **Path stripping problems**: Use `--diffstat` to see target paths, then adjust `--strip` level
2. **Permission errors**: Ensure write access to target files and directories
3. **Network timeouts**: Use local files or increase timeout settings
4. **Encoding issues**: Ensure patch files use UTF-8 or compatible encoding

### Debug Output

```bash
# Enable debug mode for detailed information
python -m patch --debug changes.patch

# Example debug output:
# DEBUG: Loading patch from changes.patch
# DEBUG: Detected patch type: git
# DEBUG: Found 3 file patches
# DEBUG: Processing patch for src/main.py
# DEBUG: Applying 2 hunks
# DEBUG: Hunk 1: lines 10-15 -> 10-16
# DEBUG: Hunk 2: lines 25-30 -> 26-31
# DEBUG: Successfully applied all hunks
```

## Next Steps

- Learn about [Core Classes](core.md) for programmatic access
- Explore [Application Module](application.md) for advanced operations
- See [User Guide](../user-guide/cli.md) for detailed CLI documentation
- Check [Examples](../examples/integration.md) for integration patterns
