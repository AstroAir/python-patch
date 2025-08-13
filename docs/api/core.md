# Core Module

The `patch.core` module contains the fundamental classes that represent parsed patch data and provide methods for applying changes to files.

## Class Hierarchy

```
PatchSet
├── items: List[Patch]
│
Patch
├── hunks: List[Hunk]
│
Hunk
├── text: List[bytes]
```

## PatchSet Class

::: patch.core.PatchSet
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 3
      members:
        - __init__
        - __len__
        - __iter__
        - parse
        - apply
        - revert
        - diffstat
        - findfile

## Patch Class

::: patch.core.Patch
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 3
      members:
        - __init__
        - __iter__
        - added
        - removed

## Hunk Class

::: patch.core.Hunk
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 3
      members:
        - __init__

## Usage Examples

### Working with PatchSet

```python
import patch

# Parse a patch file
patchset = patch.fromfile('changes.patch')

# Basic information
print(f"Patch type: {patchset.type}")
print(f"Number of files: {len(patchset)}")
print(f"Parse errors: {patchset.errors}")
print(f"Parse warnings: {patchset.warnings}")

# Iterate through patches
for patch_obj in patchset:
    print(f"File: {patch_obj.target.decode()}")
    print(f"  Added lines: {patch_obj.added}")
    print(f"  Removed lines: {patch_obj.removed}")
    print(f"  Hunks: {len(patch_obj.hunks)}")
```

### Inspecting Individual Patches

```python
# Get specific patch by index
first_patch = patchset.items[0]

# Or find by filename
target_patch = patchset.findfile('specific_file.py')

if target_patch:
    print(f"Source: {target_patch.source.decode()}")
    print(f"Target: {target_patch.target.decode()}")
    print(f"Type: {target_patch.type}")
    
    # Examine hunks
    for i, hunk in enumerate(target_patch):
        print(f"Hunk {i+1}:")
        print(f"  Source lines: {hunk.startsrc}-{hunk.startsrc + hunk.linessrc - 1}")
        print(f"  Target lines: {hunk.starttgt}-{hunk.starttgt + hunk.linestgt - 1}")
        print(f"  Description: {hunk.desc.decode()}")
```

### Analyzing Hunk Content

```python
for patch_obj in patchset:
    for hunk in patch_obj:
        print(f"Hunk at line {hunk.startsrc}:")
        
        # Process hunk text
        for line in hunk.text:
            line_str = line.decode('utf-8', errors='replace')
            
            if line_str.startswith('+'):
                print(f"  Added: {line_str[1:]}")
            elif line_str.startswith('-'):
                print(f"  Removed: {line_str[1:]}")
            else:
                print(f"  Context: {line_str[1:]}")
```

### Advanced PatchSet Operations

```python
import patch
import os

def analyze_patchset(filename):
    """Comprehensive analysis of a patch file."""
    
    patchset = patch.fromfile(filename)
    if not patchset:
        print("Failed to parse patch")
        return
    
    print(f"=== Patch Analysis: {filename} ===")
    print(f"Type: {patchset.type}")
    print(f"Files affected: {len(patchset)}")
    print(f"Errors: {patchset.errors}")
    print(f"Warnings: {patchset.warnings}")
    
    # Calculate totals
    total_added = sum(p.added for p in patchset)
    total_removed = sum(p.removed for p in patchset)
    total_hunks = sum(len(p.hunks) for p in patchset)
    
    print(f"Total changes: +{total_added} -{total_removed}")
    print(f"Total hunks: {total_hunks}")
    
    print("\n=== Per-file breakdown ===")
    for i, patch_obj in enumerate(patchset):
        target = patch_obj.target.decode('utf-8', errors='replace')
        print(f"{i+1:2d}. {target}")
        print(f"    Changes: +{patch_obj.added} -{patch_obj.removed}")
        print(f"    Hunks: {len(patch_obj.hunks)}")
        
        # Check if target file exists
        if os.path.exists(target):
            print(f"    Status: File exists")
        else:
            print(f"    Status: File missing")
    
    print("\n=== Diffstat ===")
    print(patchset.diffstat())

# Usage
analyze_patchset('complex-changes.patch')
```

### Conditional Application

```python
def smart_apply(patchset, **kwargs):
    """Apply patches with intelligent error handling."""
    
    # Pre-flight checks
    missing_files = []
    for patch_obj in patchset:
        target = patch_obj.target.decode('utf-8', errors='replace')
        
        # Apply strip logic to check actual target
        strip = kwargs.get('strip', 0)
        if strip > 0:
            parts = target.split('/')
            if len(parts) > strip:
                target = '/'.join(parts[strip:])
        
        if not os.path.exists(target):
            missing_files.append(target)
    
    if missing_files:
        print(f"Warning: Missing target files: {missing_files}")
        if not input("Continue anyway? (y/N): ").lower().startswith('y'):
            return False
    
    # Dry run first
    print("Testing patch application...")
    if not patchset.apply(dry_run=True, **kwargs):
        print("Dry run failed - patches would not apply cleanly")
        return False
    
    print("Dry run successful - applying patches...")
    return patchset.apply(**kwargs)

# Usage
patchset = patch.fromfile('risky.patch')
if patchset:
    success = smart_apply(patchset, strip=1)
    print(f"Application result: {success}")
```

### Creating Custom PatchSet

```python
from patch.core import PatchSet, Patch, Hunk

def create_simple_patch():
    """Create a patch programmatically."""
    
    # Create a new PatchSet
    patchset = PatchSet()
    patchset.type = 'custom'
    
    # Create a patch for a single file
    file_patch = Patch()
    file_patch.source = b'old_file.txt'
    file_patch.target = b'new_file.txt'
    file_patch.type = 'custom'
    
    # Create a hunk
    hunk = Hunk()
    hunk.startsrc = 1
    hunk.linessrc = 1
    hunk.starttgt = 1
    hunk.linestgt = 1
    hunk.desc = b'Simple replacement'
    hunk.text = [
        b'-old content',
        b'+new content'
    ]
    
    # Assemble the patch
    file_patch.hunks.append(hunk)
    patchset.items.append(file_patch)
    
    return patchset

# Create and use custom patch
custom_patch = create_simple_patch()
print(f"Created patch with {len(custom_patch)} files")
```

## Property Details

### PatchSet Properties

- __`name`__: Optional name for the patch set (usually filename)
- __`type`__: Patch format type (`'git'`, `'svn'`, `'plain'`, `'mixed'`)
- __`items`__: List of `Patch` objects, one per file
- __`errors`__: Count of fatal parsing errors
- __`warnings`__: Count of non-fatal parsing warnings

### Patch Properties

- __`source`__: Source filename as bytes (from `---` line)
- __`target`__: Target filename as bytes (from `+++` line)
- __`hunks`__: List of `Hunk` objects containing changes
- __`type`__: Patch type for this specific file
- __`header`__: Header lines preceding the file diff

### Hunk Properties

- __`startsrc`__: Starting line number in source file (1-based)
- __`linessrc`__: Number of lines from source file in this hunk
- __`starttgt`__: Starting line number in target file (1-based)
- __`linestgt`__: Number of lines in target file for this hunk
- __`invalid`__: Boolean indicating if hunk parsing failed
- __`desc`__: Description text following the `@@` line
- __`text`__: List of raw hunk content lines

## Thread Safety

The core classes are __not thread-safe__. If you need to use them in a multi-threaded environment:

```python
import threading
import copy

# Create thread-local copies
def thread_safe_apply(patchset, **kwargs):
    # Each thread gets its own copy
    local_patchset = copy.deepcopy(patchset)
    return local_patchset.apply(**kwargs)

# Or use locks
patch_lock = threading.Lock()

def locked_apply(patchset, **kwargs):
    with patch_lock:
        return patchset.apply(**kwargs)
```

## Next Steps

- Explore the [Parser Module](parser.md) for parsing details
- Learn about [Application Methods](application.md) for advanced application
- See [Utilities](utils.md) for helper functions
- Check [Examples](../examples/advanced.md) for complex usage patterns
