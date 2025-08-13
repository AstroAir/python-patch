# Python API Guide

This guide covers the Python API for Python Patch, providing detailed examples and best practices for programmatic patch handling.

## Overview

The Python Patch API is designed to be simple yet powerful, providing three main entry points and a rich object model for working with patches.

### Main API Functions

```python
import patch

# Parse from file
patchset = patch.fromfile('changes.patch')

# Parse from string/bytes
patchset = patch.fromstring(patch_content)

# Parse from URL
patchset = patch.fromurl('https://example.com/patch.diff')
```

## Basic Usage Patterns

### Simple Patch Application

```python
import patch

def apply_patch_simple(patch_file):
    """Apply a patch with basic error handling."""
    
    # Parse the patch
    patchset = patch.fromfile(patch_file)
    
    if not patchset:
        print(f"Failed to parse {patch_file}")
        return False
    
    # Apply the patch
    success = patchset.apply()
    
    if success:
        print(f"Successfully applied {len(patchset)} patches")
        return True
    else:
        print("Failed to apply some patches")
        return False

# Usage
apply_patch_simple('feature.patch')
```

### Patch with Options

```python
import patch

def apply_patch_with_options(patch_file, strip=1, target_dir=None, dry_run=False):
    """Apply a patch with various options."""
    
    patchset = patch.fromfile(patch_file)
    if not patchset:
        return False
    
    # Show what will be changed
    print(f"Patch contains {len(patchset)} file changes:")
    for p in patchset:
        filename = p.target.decode('utf-8', errors='replace')
        print(f"  {filename}: +{p.added} -{p.removed} lines")
    
    # Apply with options
    success = patchset.apply(
        strip=strip,
        root=target_dir,
        dry_run=dry_run
    )
    
    return success

# Usage examples
apply_patch_with_options('git.patch', strip=1)
apply_patch_with_options('svn.patch', strip=0, target_dir='/project')
apply_patch_with_options('test.patch', dry_run=True)  # Preview only
```

## Advanced Usage

### Comprehensive Error Handling

```python
import patch
import os
from pathlib import Path

class PatchError(Exception):
    """Custom exception for patch operations."""
    pass

def robust_patch_application(patch_source, **options):
    """Apply patches with comprehensive error handling."""
    
    try:
        # Determine source type and parse
        if isinstance(patch_source, str):
            if patch_source.startswith(('http://', 'https://')):
                # URL source
                print(f"Downloading patch from {patch_source}")
                patchset = patch.fromurl(patch_source)
            elif os.path.exists(patch_source):
                # File source
                print(f"Reading patch from {patch_source}")
                patchset = patch.fromfile(patch_source)
            else:
                # String content
                print("Parsing patch from string")
                patchset = patch.fromstring(patch_source)
        else:
            # Assume bytes content
            patchset = patch.fromstring(patch_source)
        
        if not patchset:
            raise PatchError("Failed to parse patch content")
        
        # Validate patch
        if patchset.errors > 0:
            print(f"Warning: {patchset.errors} parsing errors")
        
        if patchset.warnings > 0:
            print(f"Warning: {patchset.warnings} parsing warnings")
        
        print(f"Parsed {len(patchset)} file patches")
        
        # Pre-flight checks
        missing_files = []
        strip = options.get('strip', 0)
        root = options.get('root')
        
        for p in patchset:
            target = p.target.decode('utf-8', errors='replace')
            
            # Apply strip logic
            if strip > 0:
                parts = target.split('/')
                if len(parts) > strip:
                    target = '/'.join(parts[strip:])
            
            # Check in root directory if specified
            if root:
                target_path = Path(root) / target
            else:
                target_path = Path(target)
            
            if not target_path.exists():
                missing_files.append(str(target_path))
        
        if missing_files:
            print(f"Warning: Missing target files:")
            for f in missing_files:
                print(f"  - {f}")
            
            if not options.get('force', False):
                response = input("Continue anyway? (y/N): ")
                if not response.lower().startswith('y'):
                    raise PatchError("Aborted due to missing files")
        
        # Dry run first (unless disabled)
        if not options.get('skip_dry_run', False):
            print("Performing dry run...")
            dry_success = patchset.apply(dry_run=True, **options)
            
            if not dry_success:
                raise PatchError("Dry run failed - patches would not apply cleanly")
            
            print("Dry run successful")
        
        # Apply for real
        if options.get('dry_run', False):
            print("Dry run mode - not applying changes")
            return True
        
        print("Applying patches...")
        success = patchset.apply(**options)
        
        if success:
            print("All patches applied successfully!")
            
            # Show diffstat
            if options.get('show_stats', True):
                print("\nChanges applied:")
                print(patchset.diffstat())
            
            return True
        else:
            raise PatchError("Some patches failed to apply")
    
    except Exception as e:
        print(f"Error: {e}")
        return False

# Usage examples
robust_patch_application('feature.patch', strip=1, show_stats=True)
robust_patch_application('https://github.com/user/repo/commit/abc.patch', strip=1)
robust_patch_application(patch_content, root='/project', force=True)
```

### Patch Inspection and Analysis

```python
import patch
from collections import defaultdict

def analyze_patchset(patchset):
    """Comprehensive analysis of a PatchSet."""
    
    analysis = {
        'summary': {
            'files': len(patchset),
            'type': patchset.type,
            'errors': patchset.errors,
            'warnings': patchset.warnings,
        },
        'statistics': {
            'total_added': sum(p.added for p in patchset),
            'total_removed': sum(p.removed for p in patchset),
            'total_hunks': sum(len(p.hunks) for p in patchset),
        },
        'files': [],
        'file_types': defaultdict(int),
        'largest_changes': [],
    }
    
    # Analyze each file
    for p in patchset:
        target = p.target.decode('utf-8', errors='replace')
        
        file_info = {
            'path': target,
            'added': p.added,
            'removed': p.removed,
            'hunks': len(p.hunks),
            'net_change': p.added - p.removed,
        }
        
        analysis['files'].append(file_info)
        
        # Track file types
        if '.' in target:
            ext = target.split('.')[-1].lower()
            analysis['file_types'][ext] += 1
        else:
            analysis['file_types']['no_extension'] += 1
    
    # Find largest changes
    analysis['largest_changes'] = sorted(
        analysis['files'],
        key=lambda x: x['added'] + x['removed'],
        reverse=True
    )[:5]
    
    return analysis

def print_analysis(analysis):
    """Print formatted analysis results."""
    
    print("=== Patch Analysis ===")
    print(f"Files: {analysis['summary']['files']}")
    print(f"Type: {analysis['summary']['type']}")
    print(f"Errors: {analysis['summary']['errors']}")
    print(f"Warnings: {analysis['summary']['warnings']}")
    
    print(f"\nTotal changes: +{analysis['statistics']['total_added']} "
          f"-{analysis['statistics']['total_removed']}")
    print(f"Total hunks: {analysis['statistics']['total_hunks']}")
    
    print(f"\nFile types:")
    for ext, count in sorted(analysis['file_types'].items()):
        print(f"  .{ext}: {count} files")
    
    print(f"\nLargest changes:")
    for file_info in analysis['largest_changes']:
        print(f"  {file_info['path']}: "
              f"+{file_info['added']} -{file_info['removed']} "
              f"({file_info['hunks']} hunks)")

# Usage
patchset = patch.fromfile('large-update.patch')
if patchset:
    analysis = analyze_patchset(patchset)
    print_analysis(analysis)
```

### Conditional Application

```python
import patch
import os

def smart_patch_apply(patch_file, **options):
    """Intelligently apply patches with various safety checks."""
    
    patchset = patch.fromfile(patch_file)
    if not patchset:
        return False
    
    # Analyze the patch first
    analysis = analyze_patchset(patchset)
    
    # Safety checks
    safety_checks = {
        'large_changes': analysis['statistics']['total_added'] + 
                        analysis['statistics']['total_removed'] > 1000,
        'many_files': analysis['summary']['files'] > 50,
        'has_errors': analysis['summary']['errors'] > 0,
        'binary_files': any('.bin' in f['path'] or '.exe' in f['path'] 
                           for f in analysis['files']),
    }
    
    # Warn about risky operations
    warnings = []
    if safety_checks['large_changes']:
        warnings.append("Large number of changes detected")
    if safety_checks['many_files']:
        warnings.append("Many files will be modified")
    if safety_checks['has_errors']:
        warnings.append("Parsing errors detected")
    if safety_checks['binary_files']:
        warnings.append("Binary files detected")
    
    if warnings:
        print("⚠️  Safety warnings:")
        for warning in warnings:
            print(f"   - {warning}")
        
        if not options.get('force', False):
            response = input("Continue anyway? (y/N): ")
            if not response.lower().startswith('y'):
                print("Aborted by user")
                return False
    
    # Backup strategy for important changes
    if safety_checks['large_changes'] or safety_checks['many_files']:
        if options.get('create_backup', True):
            print("Creating backup of modified files...")
            backup_files(patchset, options.get('strip', 0))
    
    # Apply with appropriate strategy
    if safety_checks['has_errors']:
        # More careful application
        return careful_apply(patchset, **options)
    else:
        # Standard application
        return patchset.apply(**options)

def backup_files(patchset, strip=0):
    """Create backups of files that will be modified."""
    import shutil
    import tempfile
    from datetime import datetime
    
    backup_dir = f"patch_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(backup_dir, exist_ok=True)
    
    for p in patchset:
        target = p.target.decode('utf-8', errors='replace')
        
        # Apply strip logic
        if strip > 0:
            parts = target.split('/')
            if len(parts) > strip:
                target = '/'.join(parts[strip:])
        
        if os.path.exists(target):
            backup_path = os.path.join(backup_dir, target.replace('/', '_'))
            shutil.copy2(target, backup_path)
            print(f"  Backed up: {target} -> {backup_path}")
    
    print(f"Backup created in: {backup_dir}")

def careful_apply(patchset, **options):
    """Apply patches one by one with error handling."""
    
    success_count = 0
    total_count = len(patchset)
    
    for i, patch_obj in enumerate(patchset, 1):
        target = patch_obj.target.decode('utf-8', errors='replace')
        print(f"Applying patch {i}/{total_count}: {target}")
        
        # Create a temporary patchset with just this patch
        temp_patchset = patch.PatchSet()
        temp_patchset.items = [patch_obj]
        temp_patchset.type = patchset.type
        
        success = temp_patchset.apply(**options)
        
        if success:
            print(f"  ✓ Applied successfully")
            success_count += 1
        else:
            print(f"  ✗ Failed to apply")
            
            response = input("Continue with remaining patches? (y/N): ")
            if not response.lower().startswith('y'):
                break
    
    print(f"Applied {success_count}/{total_count} patches successfully")
    return success_count == total_count

# Usage
smart_patch_apply('risky.patch', strip=1, create_backup=True)
```

## Integration Patterns

### With Version Control

```python
import patch
import subprocess
import tempfile

def apply_git_patch(repo_path, patch_content, commit_message=None):
    """Apply a patch in a Git repository with proper commit."""
    
    original_dir = os.getcwd()
    
    try:
        os.chdir(repo_path)
        
        # Check if repo is clean
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            print("Warning: Repository has uncommitted changes")
            response = input("Continue anyway? (y/N): ")
            if not response.lower().startswith('y'):
                return False
        
        # Apply the patch
        patchset = patch.fromstring(patch_content)
        if not patchset:
            print("Failed to parse patch")
            return False
        
        success = patchset.apply(strip=1)
        if not success:
            print("Failed to apply patch")
            return False
        
        # Stage changes
        subprocess.run(['git', 'add', '-A'], check=True)
        
        # Commit if message provided
        if commit_message:
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            print(f"Changes committed: {commit_message}")
        else:
            print("Changes staged but not committed")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        return False
    finally:
        os.chdir(original_dir)

# Usage
with open('feature.patch', 'r') as f:
    patch_content = f.read()

apply_git_patch('/path/to/repo', patch_content, "Apply feature patch")
```

### With Testing

```python
import patch
import subprocess
import tempfile
import shutil

def test_and_apply_patch(patch_file, test_command, **options):
    """Apply patch only if tests pass afterward."""
    
    # Create a temporary copy of the current state
    with tempfile.TemporaryDirectory() as temp_dir:
        backup_dir = os.path.join(temp_dir, 'backup')
        shutil.copytree('.', backup_dir, ignore=shutil.ignore_patterns('.git'))
        
        try:
            # Apply the patch
            patchset = patch.fromfile(patch_file)
            if not patchset:
                print("Failed to parse patch")
                return False
            
            success = patchset.apply(**options)
            if not success:
                print("Failed to apply patch")
                return False
            
            print("Patch applied, running tests...")
            
            # Run tests
            result = subprocess.run(test_command, shell=True, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Tests passed - keeping changes")
                return True
            else:
                print("✗ Tests failed - reverting changes")
                print("Test output:")
                print(result.stdout)
                print(result.stderr)
                
                # Restore from backup
                for item in os.listdir('.'):
                    if item != '.git':
                        if os.path.isdir(item):
                            shutil.rmtree(item)
                        else:
                            os.remove(item)
                
                for item in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, item)
                    else:
                        shutil.copy2(src, item)
                
                return False
                
        except Exception as e:
            print(f"Error during test-and-apply: {e}")
            return False

# Usage
test_and_apply_patch('feature.patch', 'python -m pytest tests/', strip=1)
```

## Best Practices

### 1. Always Check Return Values

```python
# Good
patchset = patch.fromfile('patch.diff')
if patchset:
    success = patchset.apply()
    if success:
        print("Success!")
    else:
        print("Application failed")
else:
    print("Parse failed")

# Bad
patchset = patch.fromfile('patch.diff')
patchset.apply()  # Could fail if patchset is False
```

### 2. Use Dry Run for Safety

```python
# Always test first
if patchset.apply(dry_run=True, **options):
    # Safe to apply for real
    patchset.apply(**options)
else:
    print("Patch would fail - aborting")
```

### 3. Handle Encoding Issues

```python
def safe_decode(byte_string):
    """Safely decode bytes to string."""
    for encoding in ['utf-8', 'latin-1', 'cp1252']:
        try:
            return byte_string.decode(encoding)
        except UnicodeDecodeError:
            continue
    return byte_string.decode('utf-8', errors='replace')

# Use when working with filenames
for p in patchset:
    filename = safe_decode(p.target)
    print(f"Processing: {filename}")
```

### 4. Provide User Feedback

```python
def apply_with_progress(patchset, **options):
    """Apply patches with progress feedback."""
    
    total = len(patchset)
    print(f"Applying {total} patches...")
    
    for i, patch_obj in enumerate(patchset, 1):
        filename = patch_obj.target.decode('utf-8', errors='replace')
        print(f"[{i:3d}/{total}] {filename}")
        
        # Apply individual patch logic here
        
    print("All patches applied!")
```

## Next Steps

- Explore [Advanced Usage](advanced.md) for complex scenarios
- Check [Error Handling](error-handling.md) for robust applications
- See [Examples](../examples/basic.md) for practical use cases
