# Basic Examples

This page provides practical examples for common Python Patch use cases. These examples demonstrate real-world scenarios and best practices.

## File Operations

### Example 1: Simple Patch Application

```python
import patch
import os

def apply_simple_patch():
    """Apply a basic patch to a single file."""
    
    # Create a test file
    with open('example.txt', 'w') as f:
        f.write('Hello World\n')
    
    # Create a patch
    patch_content = """--- a/example.txt
+++ b/example.txt
@@ -1 +1 @@
-Hello World
+Hello Python Patch!
"""
    
    # Apply the patch
    patchset = patch.fromstring(patch_content)
    if patchset:
        success = patchset.apply()
        if success:
            print("Patch applied successfully!")
            
            # Verify the result
            with open('example.txt', 'r') as f:
                content = f.read()
                print(f"New content: {content.strip()}")
        else:
            print("Failed to apply patch")
    else:
        print("Failed to parse patch")

# Run the example
apply_simple_patch()
```

### Example 2: Multi-file Patch

```python
import patch
import os
import tempfile

def multi_file_example():
    """Apply patches to multiple files."""
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        
        # Create test files
        files = {
            'file1.py': 'def hello():\n    print("Hello")\n',
            'file2.py': 'def world():\n    print("World")\n'
        }
        
        for filename, content in files.items():
            with open(filename, 'w') as f:
                f.write(content)
        
        # Multi-file patch
        patch_content = """--- a/file1.py
+++ b/file1.py
@@ -1,2 +1,2 @@
 def hello():
-    print("Hello")
+    print("Hello Python!")

--- a/file2.py
+++ b/file2.py
@@ -1,2 +1,2 @@
 def world():
-    print("World")
+    print("Patch World!")
"""
        
        # Apply the patch
        patchset = patch.fromstring(patch_content)
        if patchset:
            print(f"Patch contains {len(patchset)} file changes")
            
            # Show what will be changed
            for p in patchset:
                filename = p.target.decode()
                print(f"  {filename}: +{p.added} -{p.removed} lines")
            
            # Apply changes
            success = patchset.apply()
            if success:
                print("All patches applied successfully!")
                
                # Show results
                for filename in files.keys():
                    with open(filename, 'r') as f:
                        print(f"\n{filename}:")
                        print(f.read())
            else:
                print("Some patches failed")

multi_file_example()
```

## Error Handling

### Example 3: Robust Error Handling

```python
import patch
import os
from pathlib import Path

def robust_patch_application(patch_file, target_dir=None, strip=0):
    """Apply patches with comprehensive error handling."""
    
    try:
        # Validate inputs
        if not os.path.exists(patch_file):
            raise FileNotFoundError(f"Patch file not found: {patch_file}")
        
        if target_dir and not os.path.isdir(target_dir):
            raise NotADirectoryError(f"Target directory not found: {target_dir}")
        
        # Parse the patch
        print(f"Parsing patch file: {patch_file}")
        patchset = patch.fromfile(patch_file)
        
        if not patchset:
            raise ValueError(f"Failed to parse patch file: {patch_file}")
        
        # Check for parsing issues
        if patchset.errors > 0:
            print(f"Warning: {patchset.errors} parsing errors encountered")
        
        if patchset.warnings > 0:
            print(f"Warning: {patchset.warnings} parsing warnings")
        
        print(f"Successfully parsed {len(patchset)} file patches")
        
        # Validate target files exist
        missing_files = []
        for p in patchset:
            target_path = p.target.decode('utf-8', errors='replace')
            
            # Apply strip logic
            if strip > 0:
                parts = target_path.split('/')
                if len(parts) > strip:
                    target_path = '/'.join(parts[strip:])
            
            # Check in target directory if specified
            if target_dir:
                full_path = os.path.join(target_dir, target_path)
            else:
                full_path = target_path
            
            if not os.path.exists(full_path):
                missing_files.append(full_path)
        
        if missing_files:
            print(f"Warning: Missing target files:")
            for f in missing_files:
                print(f"  - {f}")
            
            response = input("Continue anyway? (y/N): ")
            if not response.lower().startswith('y'):
                print("Aborted by user")
                return False
        
        # Dry run first
        print("Performing dry run...")
        dry_run_success = patchset.apply(
            strip=strip,
            root=target_dir,
            dry_run=True
        )
        
        if not dry_run_success:
            print("Dry run failed - patches would not apply cleanly")
            return False
        
        print("Dry run successful")
        
        # Apply for real
        print("Applying patches...")
        success = patchset.apply(strip=strip, root=target_dir)
        
        if success:
            print("All patches applied successfully!")
            
            # Show diffstat
            print("\nChanges applied:")
            print(patchset.diffstat())
            
            return True
        else:
            print("Some patches failed to apply")
            return False
    
    except FileNotFoundError as e:
        print(f"File error: {e}")
        return False
    except PermissionError as e:
        print(f"Permission error: {e}")
        return False
    except ValueError as e:
        print(f"Validation error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Usage examples
if __name__ == "__main__":
    # Apply patch to current directory
    robust_patch_application('changes.patch', strip=1)
    
    # Apply patch to specific directory
    robust_patch_application('feature.patch', target_dir='/path/to/project', strip=1)
```

## Inspection and Analysis

### Example 4: Patch Analysis Tool

```python
import patch
import sys
from pathlib import Path

def analyze_patch(patch_file):
    """Comprehensive patch analysis tool."""
    
    print(f"=== Analyzing {patch_file} ===\n")
    
    # Parse the patch
    patchset = patch.fromfile(patch_file)
    if not patchset:
        print("❌ Failed to parse patch file")
        return False
    
    # Basic information
    print(f"📊 Basic Information:")
    print(f"   Type: {patchset.type}")
    print(f"   Files: {len(patchset)}")
    print(f"   Errors: {patchset.errors}")
    print(f"   Warnings: {patchset.warnings}")
    
    # Calculate statistics
    total_added = sum(p.added for p in patchset)
    total_removed = sum(p.removed for p in patchset)
    total_hunks = sum(len(p.hunks) for p in patchset)
    
    print(f"   Total changes: +{total_added} -{total_removed}")
    print(f"   Total hunks: {total_hunks}")
    
    # File-by-file breakdown
    print(f"\n📁 File Breakdown:")
    for i, p in enumerate(patchset, 1):
        source = p.source.decode('utf-8', errors='replace') if p.source else 'N/A'
        target = p.target.decode('utf-8', errors='replace') if p.target else 'N/A'
        
        print(f"   {i:2d}. {target}")
        if source != target:
            print(f"       (from: {source})")
        print(f"       Changes: +{p.added} -{p.removed}")
        print(f"       Hunks: {len(p.hunks)}")
        
        # Check file existence
        if Path(target).exists():
            print(f"       Status: ✅ File exists")
        else:
            print(f"       Status: ❌ File missing")
    
    # Hunk details
    print(f"\n🔍 Hunk Details:")
    for i, p in enumerate(patchset, 1):
        target = p.target.decode('utf-8', errors='replace')
        print(f"   File {i}: {target}")
        
        for j, hunk in enumerate(p.hunks, 1):
            desc = hunk.desc.decode('utf-8', errors='replace') if hunk.desc else ''
            print(f"     Hunk {j}: @@ -{hunk.startsrc},{hunk.linessrc} "
                  f"+{hunk.starttgt},{hunk.linestgt} @@ {desc}")
            
            # Show first few lines of context
            for line_num, line in enumerate(hunk.text[:3]):
                line_str = line.decode('utf-8', errors='replace')
                prefix = line_str[0] if line_str else ' '
                content = line_str[1:] if len(line_str) > 1 else ''
                print(f"       {prefix} {content}")
            
            if len(hunk.text) > 3:
                print(f"       ... ({len(hunk.text) - 3} more lines)")
    
    # Diffstat
    print(f"\n📈 Diffstat:")
    diffstat = patchset.diffstat()
    for line in diffstat.split('\n'):
        if line.strip():
            print(f"   {line}")
    
    return True

def main():
    """Command-line interface for patch analysis."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_patch.py <patch_file>")
        sys.exit(1)
    
    patch_file = sys.argv[1]
    
    if not Path(patch_file).exists():
        print(f"Error: Patch file '{patch_file}' not found")
        sys.exit(1)
    
    success = analyze_patch(patch_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Batch Processing

### Example 5: Batch Patch Application

```python
import patch
import os
import glob
from pathlib import Path

def apply_patch_series(patch_directory, target_directory=None, strip=1):
    """Apply a series of patches in order."""
    
    # Find all patch files
    patch_patterns = ['*.patch', '*.diff']
    patch_files = []
    
    for pattern in patch_patterns:
        patch_files.extend(glob.glob(os.path.join(patch_directory, pattern)))
    
    if not patch_files:
        print(f"No patch files found in {patch_directory}")
        return False
    
    # Sort patches for consistent ordering
    patch_files.sort()
    
    print(f"Found {len(patch_files)} patch files:")
    for pf in patch_files:
        print(f"  - {os.path.basename(pf)}")
    
    # Apply each patch
    applied_count = 0
    failed_patches = []
    
    for patch_file in patch_files:
        patch_name = os.path.basename(patch_file)
        print(f"\n📦 Processing: {patch_name}")
        
        try:
            # Parse patch
            patchset = patch.fromfile(patch_file)
            if not patchset:
                print(f"  ❌ Failed to parse {patch_name}")
                failed_patches.append(patch_name)
                continue
            
            print(f"  📊 {len(patchset)} files, "
                  f"+{sum(p.added for p in patchset)} "
                  f"-{sum(p.removed for p in patchset)} lines")
            
            # Dry run first
            dry_success = patchset.apply(
                strip=strip,
                root=target_directory,
                dry_run=True
            )
            
            if not dry_success:
                print(f"  ❌ Dry run failed for {patch_name}")
                failed_patches.append(patch_name)
                continue
            
            # Apply for real
            success = patchset.apply(strip=strip, root=target_directory)
            
            if success:
                print(f"  ✅ Applied successfully")
                applied_count += 1
            else:
                print(f"  ❌ Application failed")
                failed_patches.append(patch_name)
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed_patches.append(patch_name)
    
    # Summary
    print(f"\n📋 Summary:")
    print(f"  Applied: {applied_count}/{len(patch_files)} patches")
    
    if failed_patches:
        print(f"  Failed patches:")
        for fp in failed_patches:
            print(f"    - {fp}")
        return False
    else:
        print(f"  🎉 All patches applied successfully!")
        return True

# Usage
if __name__ == "__main__":
    # Apply all patches in 'patches/' directory to current directory
    apply_patch_series('patches/', strip=1)
    
    # Apply to specific target directory
    # apply_patch_series('patches/', target_directory='/path/to/project', strip=1)
```

## Integration Examples

### Example 6: Git Integration

```python
import patch
import subprocess
import tempfile
import os

def apply_git_commit_patch(repo_url, commit_hash, target_dir=None):
    """Download and apply a specific Git commit as a patch."""
    
    # Construct GitHub patch URL
    if 'github.com' in repo_url:
        # Convert GitHub repo URL to patch URL
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        patch_url = f"{repo_url}/commit/{commit_hash}.patch"
    else:
        raise ValueError("Only GitHub repositories are supported in this example")
    
    print(f"Downloading patch from: {patch_url}")
    
    try:
        # Download and parse patch
        patchset = patch.fromurl(patch_url)
        
        if not patchset:
            print("Failed to download or parse patch")
            return False
        
        print(f"Downloaded patch with {len(patchset)} file changes")
        
        # Show what will be changed
        print("Changes preview:")
        print(patchset.diffstat())
        
        # Confirm application
        response = input("\nApply this patch? (y/N): ")
        if not response.lower().startswith('y'):
            print("Aborted by user")
            return False
        
        # Apply with Git-style stripping
        success = patchset.apply(strip=1, root=target_dir)
        
        if success:
            print("Patch applied successfully!")
            return True
        else:
            print("Failed to apply patch")
            return False
    
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_git_patch_from_diff():
    """Create a patch file from git diff output."""
    
    try:
        # Get current git diff
        result = subprocess.run(
            ['git', 'diff', '--no-color'],
            capture_output=True,
            text=True,
            check=True
        )
        
        if not result.stdout:
            print("No changes to create patch from")
            return None
        
        # Save to patch file
        patch_file = 'current-changes.patch'
        with open(patch_file, 'w') as f:
            f.write(result.stdout)
        
        print(f"Created patch file: {patch_file}")
        
        # Parse and analyze the patch
        patchset = patch.fromfile(patch_file)
        if patchset:
            print(f"Patch contains {len(patchset)} file changes")
            print("Diffstat:")
            print(patchset.diffstat())
        
        return patch_file
    
    except subprocess.CalledProcessError:
        print("Error: Not in a git repository or git command failed")
        return None
    except FileNotFoundError:
        print("Error: git command not found")
        return None

# Usage examples
if __name__ == "__main__":
    # Apply a specific commit from GitHub
    apply_git_commit_patch(
        'https://github.com/user/repo',
        'abc123def456',
        target_dir='/path/to/project'
    )
    
    # Create patch from current git diff
    create_git_patch_from_diff()
```

These examples demonstrate the flexibility and power of Python Patch for various real-world scenarios. Each example includes error handling and user feedback to make them suitable for production use.

## Next Steps

- Explore [Advanced Examples](advanced.md) for more complex scenarios
- Learn about [Integration Examples](integration.md) with other tools
- Check the [User Guide](../user-guide/api.md) for detailed API documentation
