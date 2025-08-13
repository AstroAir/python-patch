# API Module

The `patch.api` module provides the main entry points for parsing patches from various sources. These functions are the primary interface for most users of the library.

::: patch.api.fromfile
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.api.fromstring
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.api.fromurl
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Usage Examples

### Basic File Parsing

```python
import patch

# Parse a patch file
patchset = patch.fromfile('changes.patch')

if patchset:
    print(f"Successfully parsed {len(patchset)} patches")
    
    # Apply with path stripping
    success = patchset.apply(strip=1)
    
    if success:
        print("All patches applied successfully")
    else:
        print("Some patches failed to apply")
else:
    print("Failed to parse patch file")
```

### String/Bytes Parsing

```python
import patch

# Patch content as string
patch_content = """--- a/example.py
+++ b/example.py
@@ -1,3 +1,3 @@
 def hello():
-    print("Hello World")
+    print("Hello Python Patch!")
     return True"""

# Parse from string
patchset = patch.fromstring(patch_content)

if patchset:
    print(f"Parsed {len(patchset)} patches from string")
    
    # Inspect the patch
    for patch_obj in patchset:
        print(f"Target file: {patch_obj.target.decode()}")
        print(f"Number of hunks: {len(patch_obj.hunks)}")
```

### URL-based Parsing

```python
import patch
from urllib.error import URLError, HTTPError

# Download and parse patch from GitHub
url = "https://github.com/user/repo/commit/abc123.patch"

try:
    patchset = patch.fromurl(url)
    
    if patchset:
        print(f"Downloaded and parsed {len(patchset)} patches")
        
        # Show diffstat before applying
        print("Changes preview:")
        print(patchset.diffstat())
        
        # Apply with confirmation
        if input("Apply patches? (y/N): ").lower() == 'y':
            success = patchset.apply(strip=1)
            print(f"Application result: {success}")
    else:
        print("Failed to parse downloaded patch")
        
except HTTPError as e:
    print(f"HTTP error downloading patch: {e}")
except URLError as e:
    print(f"URL error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Advanced Error Handling

```python
import patch
import os

def safe_patch_from_file(filename):
    """Safely load a patch file with comprehensive error handling."""
    
    # Check file existence and readability
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Patch file not found: {filename}")
    
    if not os.access(filename, os.R_OK):
        raise PermissionError(f"Cannot read patch file: {filename}")
    
    # Check file size (avoid loading huge files)
    file_size = os.path.getsize(filename)
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise ValueError(f"Patch file too large: {file_size} bytes")
    
    # Parse the patch
    try:
        patchset = patch.fromfile(filename)
        
        if not patchset:
            raise ValueError(f"Failed to parse patch file: {filename}")
        
        # Check for parsing errors
        if patchset.errors > 0:
            print(f"Warning: {patchset.errors} parsing errors encountered")
        
        if patchset.warnings > 0:
            print(f"Warning: {patchset.warnings} parsing warnings")
        
        return patchset
        
    except Exception as e:
        raise RuntimeError(f"Error parsing patch file {filename}: {e}")

# Usage
try:
    patchset = safe_patch_from_file('risky.patch')
    print(f"Safely loaded {len(patchset)} patches")
except (FileNotFoundError, PermissionError, ValueError, RuntimeError) as e:
    print(f"Error: {e}")
```

### Batch Processing

```python
import patch
import glob
import os

def apply_patch_directory(patch_dir, target_dir=None, strip=1):
    """Apply all patches in a directory."""
    
    # Find all patch files
    patch_files = glob.glob(os.path.join(patch_dir, "*.patch"))
    patch_files.extend(glob.glob(os.path.join(patch_dir, "*.diff")))
    
    if not patch_files:
        print(f"No patch files found in {patch_dir}")
        return False
    
    print(f"Found {len(patch_files)} patch files")
    
    # Sort for consistent application order
    patch_files.sort()
    
    success_count = 0
    
    for patch_file in patch_files:
        print(f"\nProcessing: {os.path.basename(patch_file)}")
        
        try:
            patchset = patch.fromfile(patch_file)
            
            if not patchset:
                print(f"  ✗ Failed to parse {patch_file}")
                continue
            
            print(f"  Found {len(patchset)} file changes")
            
            # Apply patches
            apply_kwargs = {'strip': strip}
            if target_dir:
                apply_kwargs['root'] = target_dir
            
            success = patchset.apply(**apply_kwargs)
            
            if success:
                print(f"  ✓ Applied successfully")
                success_count += 1
            else:
                print(f"  ✗ Application failed")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print(f"\nSummary: {success_count}/{len(patch_files)} patches applied successfully")
    return success_count == len(patch_files)

# Usage
apply_patch_directory('patches/', target_dir='/path/to/project', strip=1)
```

## Return Value Details

### Success Case

When parsing succeeds, all functions return a `PatchSet` object:

```python
patchset = patch.fromfile('valid.patch')
print(type(patchset))  # <class 'patch.core.PatchSet'>
print(len(patchset))   # Number of file patches
print(patchset.errors) # Should be 0 for successful parsing
```

### Failure Case

When parsing fails, all functions return `False`:

```python
patchset = patch.fromfile('invalid.patch')
print(patchset)        # False
print(type(patchset))  # <class 'bool'>

# Safe checking
if patchset:
    # This block won't execute on failure
    patchset.apply()
```

### Partial Success

Even with some parsing warnings, a `PatchSet` may be returned:

```python
patchset = patch.fromfile('problematic.patch')

if patchset:
    print(f"Errors: {patchset.errors}")
    print(f"Warnings: {patchset.warnings}")
    
    # Decide whether to proceed based on error count
    if patchset.errors == 0:
        patchset.apply()
    else:
        print("Too many errors - aborting")
```

## Performance Considerations

### Memory Usage

- `fromfile()` loads the entire file into memory
- `fromstring()` works with in-memory data
- `fromurl()` downloads the entire content before parsing

For very large patches, consider streaming approaches or splitting into smaller files.

### Network Timeouts

When using `fromurl()`, consider setting timeouts:

```python
import socket
import patch

# Set global socket timeout
socket.setdefaulttimeout(30)  # 30 seconds

try:
    patchset = patch.fromurl('https://slow-server.com/large.patch')
except socket.timeout:
    print("Download timed out")
```

## Next Steps

- Learn about the [Core Classes](core.md) returned by these functions
- Explore [Application Methods](application.md) for applying patches
- See [Examples](../examples/basic.md) for more usage patterns
