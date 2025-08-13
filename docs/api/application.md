# Application Module

The `patch.application` module provides functionality for applying patches to files, generating diffstats, and managing patch operations. It contains the core logic for transforming files based on parsed patch data.

## Functions

::: patch.application.diffstat
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.application.findfile
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.application.can_patch
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.application.patch_stream
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.application.write_hunks
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Usage Examples

### Generating Diffstats

```python
import patch
from patch.application import diffstat

# Parse a patch file
patchset = patch.fromfile('changes.patch')

if patchset:
    # Generate and display diffstat
    stats = diffstat(patchset)
    print("Changes summary:")
    print(stats)
    
    # Example output:
    # src/main.py    |  15 +++++++++------
    # tests/test.py  |   8 ++++++++
    # README.md      |   3 ++-
    # 3 files changed, 19 insertions(+), 7 deletions(-)
```

### File Matching and Validation

```python
import patch
from patch.application import findfile, can_patch

# Parse patch
patchset = patch.fromfile('changes.patch')

if patchset:
    # Find specific file in patchset
    target_patch = findfile(patchset, 'src/main.py')
    
    if target_patch:
        print(f"Found patch for src/main.py")
        print(f"Changes: +{target_patch.added} -{target_patch.removed}")
        
        # Check if file can be patched
        if can_patch('src/main.py', target_patch.hunks):
            print("File can be patched successfully")
        else:
            print("File cannot be patched (conflicts detected)")
```

### Stream-based Patch Application

```python
from patch.application import patch_stream
from io import BytesIO

def apply_patch_to_content(original_content, hunks):
    """Apply hunks to content without touching filesystem."""
    
    # Create input stream
    input_stream = BytesIO(original_content)
    
    # Apply patches and collect output
    patched_lines = list(patch_stream(input_stream, hunks))
    
    # Combine into final content
    return b''.join(patched_lines)

# Usage
original = b"line1\nold line\nline3\n"
# Assume we have hunks from a parsed patch
patched = apply_patch_to_content(original, patch_obj.hunks)
print(f"Patched content: {patched}")
```

### Advanced File Operations

```python
import patch
from patch.application import write_hunks
import tempfile
import os

def safe_patch_application(patchset, backup=True):
    """Apply patches with backup and rollback capability."""
    
    applied_files = []
    backup_files = []
    
    try:
        for patch_obj in patchset:
            target_file = patch_obj.target.decode('utf-8')
            
            # Create backup if requested
            if backup and os.path.exists(target_file):
                backup_file = f"{target_file}.backup"
                shutil.copy2(target_file, backup_file)
                backup_files.append((target_file, backup_file))
            
            # Apply patch using write_hunks
            temp_file = f"{target_file}.tmp"
            success = write_hunks(target_file, temp_file, patch_obj.hunks)
            
            if success:
                # Replace original with patched version
                if os.path.exists(target_file):
                    os.remove(target_file)
                os.rename(temp_file, target_file)
                applied_files.append(target_file)
            else:
                # Clean up temp file on failure
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                raise RuntimeError(f"Failed to apply patch to {target_file}")
        
        print(f"Successfully applied patches to {len(applied_files)} files")
        return True
        
    except Exception as e:
        print(f"Error during patch application: {e}")
        
        # Rollback on failure
        if backup:
            print("Rolling back changes...")
            for target_file, backup_file in backup_files:
                if os.path.exists(backup_file):
                    shutil.copy2(backup_file, target_file)
                    os.remove(backup_file)
        
        return False
    
    finally:
        # Clean up backup files on success
        if backup:
            for _, backup_file in backup_files:
                if os.path.exists(backup_file):
                    os.remove(backup_file)

# Usage
patchset = patch.fromfile('risky-changes.patch')
if patchset:
    success = safe_patch_application(patchset, backup=True)
```

### Patch Validation and Testing

```python
import patch
from patch.application import can_patch
import os

def validate_patchset(patchset, root_dir=None):
    """Validate that all patches in a patchset can be applied."""
    
    validation_results = []
    
    for i, patch_obj in enumerate(patchset):
        target_path = patch_obj.target.decode('utf-8')
        
        # Apply root directory if specified
        if root_dir:
            target_path = os.path.join(root_dir, target_path)
        
        result = {
            'index': i,
            'target': target_path,
            'exists': os.path.exists(target_path),
            'can_patch': False,
            'issues': []
        }
        
        # Check if file exists
        if not result['exists']:
            result['issues'].append('Target file does not exist')
        else:
            # Check if patch can be applied
            try:
                result['can_patch'] = can_patch(target_path, patch_obj.hunks)
                if not result['can_patch']:
                    result['issues'].append('Patch conflicts detected')
            except Exception as e:
                result['issues'].append(f'Validation error: {e}')
        
        validation_results.append(result)
    
    return validation_results

def print_validation_report(results):
    """Print a formatted validation report."""
    
    print("Patch Validation Report")
    print("=" * 50)
    
    total_patches = len(results)
    valid_patches = sum(1 for r in results if r['can_patch'])
    
    for result in results:
        status = "✓" if result['can_patch'] else "✗"
        print(f"{status} {result['target']}")
        
        if result['issues']:
            for issue in result['issues']:
                print(f"    - {issue}")
    
    print(f"\nSummary: {valid_patches}/{total_patches} patches can be applied")
    return valid_patches == total_patches

# Usage
patchset = patch.fromfile('complex-changes.patch')
if patchset:
    results = validate_patchset(patchset, root_dir='/project')
    all_valid = print_validation_report(results)
    
    if all_valid:
        print("All patches validated - safe to apply")
        patchset.apply(root='/project')
    else:
        print("Validation failed - manual review required")
```

## Internal Functions

The module also contains several internal functions used by the core classes:

- **`match_file_hunks()`** - Match hunks to file content for validation
- **`reverse_patchset()`** - Create reverse patches for rollback operations
- **`dump_patchset()`** - Serialize patchset back to diff format

## Error Handling

### Common Application Errors

```python
import patch
from patch.application import can_patch

def robust_patch_check(filename, hunks):
    """Robustly check if a file can be patched."""
    
    try:
        # Check file accessibility
        if not os.path.exists(filename):
            return False, "File does not exist"
        
        if not os.access(filename, os.R_OK):
            return False, "File is not readable"
        
        if not os.access(filename, os.W_OK):
            return False, "File is not writable"
        
        # Check patch applicability
        if can_patch(filename, hunks):
            return True, "Patch can be applied"
        else:
            return False, "Patch conflicts with current file content"
            
    except PermissionError:
        return False, "Permission denied"
    except IOError as e:
        return False, f"I/O error: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"

# Usage
for patch_obj in patchset:
    target = patch_obj.target.decode('utf-8')
    can_apply, reason = robust_patch_check(target, patch_obj.hunks)
    
    if can_apply:
        print(f"✓ {target}: {reason}")
    else:
        print(f"✗ {target}: {reason}")
```

## Performance Optimization

### Large File Handling

```python
from patch.application import patch_stream
import mmap

def patch_large_file(filename, hunks, output_filename=None):
    """Efficiently patch large files using memory mapping."""
    
    if output_filename is None:
        output_filename = filename
    
    # Use memory mapping for large files
    with open(filename, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped_file:
            # Create a BytesIO wrapper for the memory-mapped file
            stream_wrapper = BytesIO(mmapped_file[:])
            
            # Apply patches
            patched_lines = list(patch_stream(stream_wrapper, hunks))
    
    # Write result
    with open(output_filename, 'wb') as f:
        f.writelines(patched_lines)
    
    return True

# Usage for files > 100MB
success = patch_large_file('huge_file.txt', patch_obj.hunks)
```

## Next Steps

- Explore [Core Classes](core.md) for patch data structures
- Learn about [CLI Module](cli.md) for command-line usage
- See [Utilities](utils.md) for path handling functions
- Check [Examples](../examples/advanced.md) for complex application scenarios
