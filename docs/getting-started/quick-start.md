# Quick Start

Get up and running with Python Patch in minutes! This guide covers the most common use cases to help you start applying patches right away.

## Your First Patch

Let's start with a simple example. Create a test file and apply a basic patch:

### Step 1: Create a Test File

```bash
echo "Hello World" > test.txt
```

### Step 2: Create a Patch

```bash
cat > changes.patch << 'EOF'
--- a/test.txt
+++ b/test.txt
@@ -1 +1 @@
-Hello World
+Hello Python Patch!
EOF
```

### Step 3: Apply the Patch

=== "Command Line"

    ```bash
    patch changes.patch
    ```

=== "Python API"

    ```python
    import patch
    
    # Apply the patch
    patchset = patch.fromfile('changes.patch')
    if patchset:
        success = patchset.apply()
        print(f"Patch applied successfully: {success}")
    ```

### Step 4: Verify the Result

```bash
cat test.txt
# Output: Hello Python Patch!
```

Congratulations! You've successfully applied your first patch.

## Common Operations

### Applying Patches with Strip Levels

When patches contain path prefixes, use the `--strip` option:

```bash
# Patch with paths like a/src/file.py and b/src/file.py
patch --strip=1 feature.patch

# Patch with deeper paths
patch --strip=2 deep-path.patch
```

In Python:

```python
patchset = patch.fromfile('feature.patch')
patchset.apply(strip=1)
```

### Dry Run (Preview Changes)

Preview what a patch would do without making changes:

```bash
# Command line
patch --dry-run changes.patch

# Python API
patchset = patch.fromfile('changes.patch')
success = patchset.apply(dry_run=True)
```

### Reversing Patches

Undo changes by reversing a patch:

```bash
# Command line
patch --reverse changes.patch

# Python API
patchset = patch.fromfile('changes.patch')
patchset.revert()
```

### Working with Different Patch Formats

Python Patch automatically detects and handles various patch formats:

=== "Git Format"

    ```bash
    # Git patches often need strip=1
    patch --strip=1 git-feature.patch
    ```

=== "SVN Format"

    ```bash
    # SVN patches typically work with default settings
    patch svn-changes.patch
    ```

=== "Mercurial Format"

    ```bash
    # HG patches may need different strip levels
    patch --strip=1 hg-update.patch
    ```

## Real-World Examples

### Example 1: Applying a GitHub Patch

Download and apply a patch from GitHub:

```python
import patch

# Download patch from GitHub commit
url = "https://github.com/user/repo/commit/abc123.patch"
patchset = patch.fromurl(url)

if patchset:
    print(f"Downloaded patch with {len(patchset)} files")
    success = patchset.apply(strip=1)
    print(f"Applied successfully: {success}")
```

### Example 2: Batch Processing

Apply multiple patches in sequence:

```python
import patch
import glob

# Apply all patches in a directory
patch_files = glob.glob("patches/*.patch")

for patch_file in sorted(patch_files):
    print(f"Applying {patch_file}...")
    patchset = patch.fromfile(patch_file)
    
    if patchset:
        success = patchset.apply(strip=1)
        if success:
            print(f"✓ {patch_file} applied successfully")
        else:
            print(f"✗ {patch_file} failed to apply")
            break
    else:
        print(f"✗ Failed to parse {patch_file}")
        break
```

### Example 3: Inspecting Patches

Analyze patch contents before applying:

```python
import patch

patchset = patch.fromfile('large-update.patch')

if patchset:
    print(f"Patch contains {len(patchset)} files:")
    
    for p in patchset:
        print(f"  {p.target}: +{p.added} -{p.removed} lines")
        print(f"    {len(p.hunks)} hunks")
    
    # Show diffstat
    print("\nDiffstat:")
    print(patchset.diffstat())
    
    # Apply if everything looks good
    if input("Apply patch? (y/N): ").lower() == 'y':
        patchset.apply(strip=1)
```

## Error Handling

Always handle potential errors when working with patches:

```python
import patch

try:
    patchset = patch.fromfile('changes.patch')
    
    if not patchset:
        print("Failed to parse patch file")
        exit(1)
    
    # Check if files exist before applying
    for p in patchset:
        if not os.path.exists(p.source):
            print(f"Warning: Source file {p.source} not found")
    
    success = patchset.apply(strip=1)
    
    if success:
        print("All patches applied successfully!")
    else:
        print("Some patches failed to apply")
        
except FileNotFoundError:
    print("Patch file not found")
except PermissionError:
    print("Permission denied - check file permissions")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Best Practices

1. **Always use dry run first** for important files
2. **Backup your files** before applying patches
3. **Check patch format** and adjust strip levels accordingly
4. **Validate results** after applying patches
5. **Use version control** to track changes

## Next Steps

Now that you've mastered the basics:

- Learn about [Basic Usage](basic-usage.md) patterns
- Explore the [Command Line Interface](../user-guide/cli.md) in detail
- Dive into the [Python API](../user-guide/api.md) documentation
- Check out more [Examples](../examples/basic.md)
