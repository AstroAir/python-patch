# Basic Usage

This guide covers the fundamental concepts and common usage patterns for Python Patch. After reading this, you'll understand how to effectively use both the command-line interface and Python API.

## Understanding Patches

### What is a Unified Diff?

A unified diff is a format for representing changes between two files. It shows:

- **Context lines**: Unchanged lines around modifications
- **Additions**: Lines prefixed with `+`
- **Deletions**: Lines prefixed with `-`
- **File headers**: Source and target file paths

Example unified diff:

```diff
--- a/example.py
+++ b/example.py
@@ -1,4 +1,4 @@
 def hello():
-    print("Hello World")
+    print("Hello Python Patch!")
     return True
```

### Patch Components

A patch file can contain multiple file changes, each with:

- **File header**: Shows source and target paths
- **Hunks**: Individual change blocks within a file
- **Context**: Surrounding unchanged lines for accurate placement

## Command Line Interface

### Basic Syntax

```bash
patch [OPTIONS] PATCH_FILE
```

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--strip=N` | Remove N path components | `--strip=1` |
| `--dry-run` | Preview changes without applying | `--dry-run` |
| `--reverse` | Reverse/undo a patch | `--reverse` |
| `--verbose` | Show detailed output | `--verbose` |
| `--directory=DIR` | Apply patches relative to directory | `--directory=/path/to/project` |

### Examples

```bash
# Basic patch application
patch changes.patch

# Apply with path stripping
patch --strip=1 feature.patch

# Preview changes
patch --dry-run --verbose update.patch

# Apply to specific directory
patch --directory=/home/user/project --strip=1 fix.patch

# Reverse a patch
patch --reverse bugfix.patch
```

## Python API

### Core Functions

Python Patch provides three main functions for loading patches:

#### `patch.fromfile(filename)`

Load a patch from a file:

```python
import patch

patchset = patch.fromfile('changes.patch')
if patchset:
    print(f"Loaded {len(patchset)} file changes")
```

#### `patch.fromstring(content)`

Parse a patch from a string or bytes:

```python
patch_content = """--- a/file.txt
+++ b/file.txt
@@ -1 +1 @@
-old content
+new content"""

patchset = patch.fromstring(patch_content)
```

#### `patch.fromurl(url)`

Download and parse a patch from a URL:

```python
url = "https://github.com/user/repo/commit/abc123.patch"
patchset = patch.fromurl(url)
```

### Working with PatchSets

A `PatchSet` is a collection of file patches:

```python
patchset = patch.fromfile('multi-file.patch')

# Basic information
print(f"Files changed: {len(patchset)}")
print(f"Total additions: {sum(p.added for p in patchset)}")
print(f"Total deletions: {sum(p.removed for p in patchset)}")

# Iterate through individual patches
for file_patch in patchset:
    print(f"File: {file_patch.target}")
    print(f"  Hunks: {len(file_patch.hunks)}")
    print(f"  Changes: +{file_patch.added} -{file_patch.removed}")
```

### Applying Patches

#### Basic Application

```python
patchset = patch.fromfile('changes.patch')
success = patchset.apply()

if success:
    print("All patches applied successfully")
else:
    print("Some patches failed to apply")
```

#### Advanced Application Options

```python
success = patchset.apply(
    strip=1,                    # Strip path components
    root='/path/to/project',    # Apply relative to directory
    dry_run=True               # Preview without applying
)
```

### Error Handling Patterns

#### Robust Patch Loading

```python
def load_patch_safely(filename):
    try:
        patchset = patch.fromfile(filename)
        if not patchset:
            print(f"Failed to parse {filename}")
            return None
        return patchset
    except FileNotFoundError:
        print(f"Patch file {filename} not found")
        return None
    except PermissionError:
        print(f"Permission denied reading {filename}")
        return None
    except Exception as e:
        print(f"Unexpected error loading {filename}: {e}")
        return None
```

#### Validation Before Application

```python
def validate_and_apply(patchset, strip=0):
    # Check if target files exist
    missing_files = []
    for p in patchset:
        target_path = p.target
        if strip > 0:
            # Simulate path stripping
            parts = target_path.split('/')
            if len(parts) > strip:
                target_path = '/'.join(parts[strip:])
        
        if not os.path.exists(target_path):
            missing_files.append(target_path)
    
    if missing_files:
        print(f"Missing target files: {missing_files}")
        return False
    
    # Apply patches
    return patchset.apply(strip=strip)
```

## Working with Different Patch Formats

### Git Patches

Git patches typically include path prefixes that need stripping:

```python
# Git format usually needs strip=1
patchset = patch.fromfile('git-commit.patch')
success = patchset.apply(strip=1)
```

### SVN Patches

Subversion patches often work with default settings:

```python
patchset = patch.fromfile('svn-diff.patch')
success = patchset.apply()  # Usually no stripping needed
```

### Mercurial Patches

Mercurial patches may vary in format:

```python
patchset = patch.fromfile('hg-export.patch')
# Try different strip levels if needed
for strip_level in [0, 1, 2]:
    if patchset.apply(strip=strip_level, dry_run=True):
        print(f"Use strip level: {strip_level}")
        break
```

## Inspecting Patch Contents

### Detailed Analysis

```python
def analyze_patch(filename):
    patchset = patch.fromfile(filename)
    if not patchset:
        return
    
    print(f"Patch Analysis: {filename}")
    print(f"Files affected: {len(patchset)}")
    
    total_added = sum(p.added for p in patchset)
    total_removed = sum(p.removed for p in patchset)
    
    print(f"Total changes: +{total_added} -{total_removed}")
    print("\nPer-file breakdown:")
    
    for p in patchset:
        print(f"  {p.target}:")
        print(f"    Hunks: {len(p.hunks)}")
        print(f"    Lines: +{p.added} -{p.removed}")
        
        # Show hunk details
        for i, hunk in enumerate(p.hunks):
            print(f"    Hunk {i+1}: @@ -{hunk.startsrc},{hunk.linessrc} "
                  f"+{hunk.starttgt},{hunk.linestgt} @@")
```

### Diffstat Generation

```python
patchset = patch.fromfile('changes.patch')
print("Diffstat:")
print(patchset.diffstat())
```

## Best Practices

### 1. Always Validate Input

```python
def safe_patch_apply(filename, **kwargs):
    if not os.path.exists(filename):
        raise FileNotFoundError(f"Patch file {filename} not found")
    
    patchset = patch.fromfile(filename)
    if not patchset:
        raise ValueError(f"Invalid patch format in {filename}")
    
    return patchset.apply(**kwargs)
```

### 2. Use Dry Run for Safety

```python
# Always test first
if patchset.apply(dry_run=True, **options):
    # Safe to apply
    patchset.apply(**options)
else:
    print("Patch would fail - aborting")
```

### 3. Handle Path Stripping Intelligently

```python
def find_best_strip_level(patchset, max_strip=3):
    for strip in range(max_strip + 1):
        if patchset.apply(strip=strip, dry_run=True):
            return strip
    return None
```

### 4. Backup Before Applying

```python
import shutil
import tempfile

def apply_with_backup(patchset, **kwargs):
    # Create backup
    backup_dir = tempfile.mkdtemp(prefix='patch_backup_')
    
    try:
        # Backup affected files
        for p in patchset:
            if os.path.exists(p.target):
                shutil.copy2(p.target, backup_dir)
        
        # Apply patch
        success = patchset.apply(**kwargs)
        
        if success:
            print(f"Patch applied successfully. Backup in: {backup_dir}")
        else:
            # Restore from backup
            for backup_file in os.listdir(backup_dir):
                shutil.copy2(
                    os.path.join(backup_dir, backup_file),
                    backup_file
                )
            print("Patch failed - files restored from backup")
        
        return success
        
    except Exception as e:
        print(f"Error during patch application: {e}")
        return False
```

## Next Steps

Now that you understand the basics:

- Explore the [Command Line Interface](../user-guide/cli.md) in detail
- Learn advanced [Python API](../user-guide/api.md) techniques
- Check out practical [Examples](../examples/basic.md)
- Read about [Error Handling](../user-guide/error-handling.md) strategies
