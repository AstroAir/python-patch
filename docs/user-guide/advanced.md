# Advanced Usage

This guide covers advanced features and techniques for working with Python Patch, including complex patch scenarios, performance optimization, and integration patterns.

## Advanced Patch Operations

### Conditional Patch Application

```python
import patch
import os

def conditional_apply(patchset, conditions=None):
    """Apply patches based on custom conditions."""
    
    conditions = conditions or {}
    applied_count = 0
    
    for patch_obj in patchset:
        target_file = patch_obj.target.decode('utf-8')
        
        # Check file-specific conditions
        should_apply = True
        
        # Size-based conditions
        if 'max_file_size' in conditions:
            if os.path.exists(target_file):
                file_size = os.path.getsize(target_file)
                if file_size > conditions['max_file_size']:
                    print(f"Skipping {target_file}: too large ({file_size} bytes)")
                    should_apply = False
        
        # Extension-based conditions
        if 'allowed_extensions' in conditions:
            _, ext = os.path.splitext(target_file)
            if ext not in conditions['allowed_extensions']:
                print(f"Skipping {target_file}: extension {ext} not allowed")
                should_apply = False
        
        # Change size conditions
        if 'max_changes' in conditions:
            total_changes = patch_obj.added + patch_obj.removed
            if total_changes > conditions['max_changes']:
                print(f"Skipping {target_file}: too many changes ({total_changes})")
                should_apply = False
        
        if should_apply:
            # Apply individual patch
            temp_patchset = patch.core.PatchSet()
            temp_patchset.items = [patch_obj]
            
            if temp_patchset.apply():
                applied_count += 1
                print(f"✓ Applied patch to {target_file}")
            else:
                print(f"✗ Failed to apply patch to {target_file}")
    
    return applied_count

# Usage
patchset = patch.fromfile('large-changes.patch')
if patchset:
    conditions = {
        'max_file_size': 1024 * 1024,  # 1MB limit
        'allowed_extensions': ['.py', '.txt', '.md'],
        'max_changes': 100  # Max 100 line changes per file
    }
    
    applied = conditional_apply(patchset, conditions)
    print(f"Applied {applied}/{len(patchset)} patches")
```

### Patch Transformation

```python
import patch
import re

def transform_patchset(patchset, transformations):
    """Apply transformations to patch content before application."""
    
    for patch_obj in patchset:
        for hunk in patch_obj.hunks:
            # Transform each line in the hunk
            for i, line in enumerate(hunk.text):
                original_line = line
                
                # Apply each transformation
                for transform_func in transformations:
                    line = transform_func(line)
                
                # Update the hunk if line changed
                if line != original_line:
                    hunk.text[i] = line
    
    return patchset

def replace_tabs_with_spaces(line):
    """Transform tabs to spaces."""
    if line.startswith((b'+', b'-')):
        prefix = line[:1]
        content = line[1:]
        # Replace tabs with 4 spaces
        content = content.replace(b'\t', b'    ')
        return prefix + content
    return line

def update_copyright_year(line):
    """Update copyright years in patches."""
    if line.startswith((b'+', b'-')):
        prefix = line[:1]
        content = line[1:]
        # Update copyright year
        content = re.sub(b'Copyright \\(c\\) \\d{4}', b'Copyright (c) 2024', content)
        return prefix + content
    return line

# Usage
patchset = patch.fromfile('legacy-code.patch')
if patchset:
    transformations = [
        replace_tabs_with_spaces,
        update_copyright_year
    ]
    
    transformed_patchset = transform_patchset(patchset, transformations)
    success = transformed_patchset.apply()
```

### Multi-Stage Patch Application

```python
import patch
import tempfile
import shutil

def staged_patch_application(patch_files, target_dir):
    """Apply multiple patches in stages with rollback capability."""
    
    # Create staging directory
    with tempfile.TemporaryDirectory() as staging_dir:
        # Copy target directory to staging
        shutil.copytree(target_dir, os.path.join(staging_dir, 'work'))
        work_dir = os.path.join(staging_dir, 'work')
        
        applied_patches = []
        
        try:
            for patch_file in patch_files:
                print(f"Applying stage: {patch_file}")
                
                # Parse patch
                patchset = patch.fromfile(patch_file)
                if not patchset:
                    raise RuntimeError(f"Failed to parse {patch_file}")
                
                # Apply to staging directory
                success = patchset.apply(root=work_dir)
                if not success:
                    raise RuntimeError(f"Failed to apply {patch_file}")
                
                applied_patches.append(patch_file)
                print(f"✓ Stage {len(applied_patches)} completed")
            
            # All stages successful - copy back to target
            print("All stages successful, finalizing...")
            
            # Backup original
            backup_dir = f"{target_dir}.backup"
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            shutil.copytree(target_dir, backup_dir)
            
            # Replace with staged version
            shutil.rmtree(target_dir)
            shutil.copytree(work_dir, target_dir)
            
            print(f"Successfully applied {len(applied_patches)} patch stages")
            return True
            
        except Exception as e:
            print(f"Stage application failed: {e}")
            print(f"Successfully applied stages: {applied_patches}")
            return False

# Usage
patch_files = [
    'stage1-refactor.patch',
    'stage2-features.patch', 
    'stage3-cleanup.patch'
]

success = staged_patch_application(patch_files, '/project')
```

## Performance Optimization

### Memory-Efficient Processing

```python
import patch
from patch.application import patch_stream
import mmap

def memory_efficient_patch(large_file, hunks, chunk_size=8192):
    """Apply patches to large files with minimal memory usage."""
    
    # Use memory mapping for input
    with open(large_file, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmapped:
            
            # Create temporary output file
            temp_output = f"{large_file}.tmp"
            
            with open(temp_output, 'wb') as output:
                # Process in chunks
                input_stream = BytesIO(mmapped[:])
                
                for chunk in patch_stream(input_stream, hunks):
                    output.write(chunk)
                    
                    # Flush periodically to avoid memory buildup
                    if output.tell() % chunk_size == 0:
                        output.flush()
    
    # Replace original with patched version
    os.replace(temp_output, large_file)
    return True

# Usage for files > 100MB
success = memory_efficient_patch('huge_dataset.txt', patch_obj.hunks)
```

### Parallel Patch Processing

```python
import patch
import concurrent.futures
import os

def parallel_patch_application(patchset, max_workers=4):
    """Apply patches in parallel for better performance."""
    
    def apply_single_patch(patch_obj):
        """Apply a single patch object."""
        target_file = patch_obj.target.decode('utf-8')
        
        try:
            # Create temporary patchset with single patch
            temp_patchset = patch.core.PatchSet()
            temp_patchset.items = [patch_obj]
            
            success = temp_patchset.apply()
            return target_file, success, None
            
        except Exception as e:
            return target_file, False, str(e)
    
    # Apply patches in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all patch jobs
        future_to_patch = {
            executor.submit(apply_single_patch, patch_obj): patch_obj 
            for patch_obj in patchset
        }
        
        # Collect results
        for future in concurrent.futures.as_completed(future_to_patch):
            target_file, success, error = future.result()
            results.append((target_file, success, error))
            
            if success:
                print(f"✓ {target_file}")
            else:
                print(f"✗ {target_file}: {error}")
    
    # Summary
    successful = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    print(f"Parallel application: {successful}/{total} patches applied")
    return successful == total

# Usage
patchset = patch.fromfile('many-files.patch')
if patchset and len(patchset) > 10:  # Only use parallel for many files
    success = parallel_patch_application(patchset, max_workers=8)
else:
    success = patchset.apply()  # Use standard application for small sets
```

## Integration Patterns

### Version Control Integration

```python
import patch
import subprocess
import tempfile

def apply_with_git_integration(patch_content, commit_message=None):
    """Apply patch and create git commit."""
    
    # Parse patch
    patchset = patch.fromstring(patch_content)
    if not patchset:
        return False, "Failed to parse patch"
    
    # Check git status
    result = subprocess.run(['git', 'status', '--porcelain'], 
                          capture_output=True, text=True)
    if result.stdout.strip():
        return False, "Working directory not clean"
    
    # Apply patch
    success = patchset.apply()
    if not success:
        return False, "Patch application failed"
    
    # Stage changes
    subprocess.run(['git', 'add', '-A'])
    
    # Create commit
    if commit_message:
        subprocess.run(['git', 'commit', '-m', commit_message])
    else:
        # Extract commit message from patch if available
        subprocess.run(['git', 'commit', '-m', 'Applied patch'])
    
    return True, "Patch applied and committed"

# Usage
with open('feature.patch', 'rb') as f:
    patch_content = f.read()

success, message = apply_with_git_integration(
    patch_content, 
    "Apply feature patch from upstream"
)
print(message)
```

### Testing Integration

```python
import patch
import subprocess
import tempfile

def test_patch_before_apply(patchset, test_command):
    """Test patches in isolation before applying to main codebase."""
    
    with tempfile.TemporaryDirectory() as test_dir:
        # Copy current directory to test environment
        shutil.copytree('.', test_dir, dirs_exist_ok=True)
        
        # Apply patches in test environment
        success = patchset.apply(root=test_dir)
        if not success:
            return False, "Patch application failed in test environment"
        
        # Run tests in test environment
        result = subprocess.run(
            test_command, 
            cwd=test_dir,
            capture_output=True, 
            text=True
        )
        
        if result.returncode != 0:
            return False, f"Tests failed: {result.stderr}"
        
        return True, "Tests passed in patched environment"

# Usage
patchset = patch.fromfile('new-feature.patch')
if patchset:
    success, message = test_patch_before_apply(
        patchset, 
        ['python', '-m', 'pytest', 'tests/']
    )
    
    if success:
        print("Tests passed - applying to main codebase")
        patchset.apply()
    else:
        print(f"Tests failed: {message}")
```

## Error Recovery

### Automatic Rollback

```python
import patch
import json
import os
from datetime import datetime

def apply_with_rollback(patchset, metadata_file='.patch_history.json'):
    """Apply patches with automatic rollback capability."""
    
    # Load existing history
    history = []
    if os.path.exists(metadata_file):
        with open(metadata_file, 'r') as f:
            history = json.load(f)
    
    # Create backup information
    backup_info = {
        'timestamp': datetime.now().isoformat(),
        'files': [],
        'patch_count': len(patchset)
    }
    
    # Backup affected files
    for patch_obj in patchset:
        target_file = patch_obj.target.decode('utf-8')
        
        if os.path.exists(target_file):
            # Create backup
            backup_file = f"{target_file}.backup.{len(history)}"
            shutil.copy2(target_file, backup_file)
            
            backup_info['files'].append({
                'original': target_file,
                'backup': backup_file,
                'size': os.path.getsize(target_file)
            })
    
    try:
        # Apply patches
        success = patchset.apply()
        
        if success:
            # Record successful application
            backup_info['status'] = 'applied'
            history.append(backup_info)
            
            # Save history
            with open(metadata_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            print(f"Patches applied successfully (backup #{len(history)})")
            return True
        else:
            raise RuntimeError("Patch application failed")
            
    except Exception as e:
        # Rollback on failure
        print(f"Error: {e}")
        print("Rolling back changes...")
        
        for file_info in backup_info['files']:
            if os.path.exists(file_info['backup']):
                shutil.copy2(file_info['backup'], file_info['original'])
                os.remove(file_info['backup'])
        
        return False

def rollback_last_patch(metadata_file='.patch_history.json'):
    """Rollback the most recent patch application."""
    
    if not os.path.exists(metadata_file):
        print("No patch history found")
        return False
    
    with open(metadata_file, 'r') as f:
        history = json.load(f)
    
    if not history:
        print("No patches to rollback")
        return False
    
    # Get last applied patch
    last_patch = history[-1]
    
    if last_patch['status'] != 'applied':
        print("Last patch was not successfully applied")
        return False
    
    # Restore files
    for file_info in last_patch['files']:
        if os.path.exists(file_info['backup']):
            shutil.copy2(file_info['backup'], file_info['original'])
            os.remove(file_info['backup'])
            print(f"Restored {file_info['original']}")
    
    # Update history
    history[-1]['status'] = 'rolled_back'
    with open(metadata_file, 'w') as f:
        json.dump(history, f, indent=2)
    
    print("Rollback completed successfully")
    return True

# Usage
patchset = patch.fromfile('risky-changes.patch')
if patchset:
    success = apply_with_rollback(patchset)
    
    if not success:
        print("Application failed - changes were rolled back")
    
    # Later, if needed:
    # rollback_last_patch()
```

## Custom Patch Formats

### Creating Custom Patches

```python
from patch.core import PatchSet, Patch, Hunk

def create_migration_patch(file_mappings):
    """Create a patch for file migrations/renames."""
    
    patchset = PatchSet()
    patchset.type = 'migration'
    
    for old_path, new_path in file_mappings.items():
        # Create rename patch
        file_patch = Patch()
        file_patch.source = old_path.encode('utf-8')
        file_patch.target = new_path.encode('utf-8')
        file_patch.type = 'rename'
        
        # Create a hunk that represents the entire file
        if os.path.exists(old_path):
            with open(old_path, 'rb') as f:
                content = f.readlines()
            
            hunk = Hunk()
            hunk.startsrc = 1
            hunk.linessrc = len(content)
            hunk.starttgt = 1
            hunk.linestgt = len(content)
            hunk.desc = b'File migration'
            
            # Mark all lines as context (no changes)
            hunk.text = [b' ' + line.rstrip(b'\n\r') for line in content]
            
            file_patch.hunks.append(hunk)
        
        patchset.items.append(file_patch)
    
    return patchset

# Usage
migrations = {
    'old_module/legacy.py': 'new_module/modern.py',
    'deprecated/utils.py': 'core/utilities.py'
}

migration_patch = create_migration_patch(migrations)
print(f"Created migration patch for {len(migration_patch)} files")
```

### Patch Serialization

```python
import patch
import pickle
import json

def serialize_patchset(patchset, format='json'):
    """Serialize patchset for storage or transmission."""
    
    if format == 'pickle':
        return pickle.dumps(patchset)
    
    elif format == 'json':
        # Convert to JSON-serializable format
        data = {
            'type': patchset.type,
            'errors': patchset.errors,
            'warnings': patchset.warnings,
            'patches': []
        }
        
        for patch_obj in patchset:
            patch_data = {
                'source': patch_obj.source.decode('utf-8', errors='replace'),
                'target': patch_obj.target.decode('utf-8', errors='replace'),
                'type': patch_obj.type,
                'added': patch_obj.added,
                'removed': patch_obj.removed,
                'hunks': []
            }
            
            for hunk in patch_obj.hunks:
                hunk_data = {
                    'startsrc': hunk.startsrc,
                    'linessrc': hunk.linessrc,
                    'starttgt': hunk.starttgt,
                    'linestgt': hunk.linestgt,
                    'desc': hunk.desc.decode('utf-8', errors='replace'),
                    'text': [line.decode('utf-8', errors='replace') for line in hunk.text]
                }
                patch_data['hunks'].append(hunk_data)
            
            data['patches'].append(patch_data)
        
        return json.dumps(data, indent=2)
    
    else:
        raise ValueError(f"Unsupported format: {format}")

def deserialize_patchset(data, format='json'):
    """Deserialize patchset from stored format."""
    
    if format == 'pickle':
        return pickle.loads(data)
    
    elif format == 'json':
        parsed = json.loads(data)
        
        # Reconstruct patchset
        patchset = PatchSet()
        patchset.type = parsed['type']
        patchset.errors = parsed['errors']
        patchset.warnings = parsed['warnings']
        
        for patch_data in parsed['patches']:
            patch_obj = Patch()
            patch_obj.source = patch_data['source'].encode('utf-8')
            patch_obj.target = patch_data['target'].encode('utf-8')
            patch_obj.type = patch_data['type']
            
            for hunk_data in patch_data['hunks']:
                hunk = Hunk()
                hunk.startsrc = hunk_data['startsrc']
                hunk.linessrc = hunk_data['linessrc']
                hunk.starttgt = hunk_data['starttgt']
                hunk.linestgt = hunk_data['linestgt']
                hunk.desc = hunk_data['desc'].encode('utf-8')
                hunk.text = [line.encode('utf-8') for line in hunk_data['text']]
                
                patch_obj.hunks.append(hunk)
            
            patchset.items.append(patch_obj)
        
        return patchset
    
    else:
        raise ValueError(f"Unsupported format: {format}")

# Usage
patchset = patch.fromfile('complex.patch')
if patchset:
    # Serialize for storage
    serialized = serialize_patchset(patchset, 'json')
    
    with open('patchset.json', 'w') as f:
        f.write(serialized)
    
    # Later, deserialize
    with open('patchset.json', 'r') as f:
        serialized = f.read()
    
    restored_patchset = deserialize_patchset(serialized, 'json')
    print(f"Restored patchset with {len(restored_patchset)} patches")
```

## Security Considerations

### Safe Patch Validation

```python
import patch
from patch.utils import xisabs, xnormpath
import os

def security_validate_patchset(patchset, allowed_paths=None, max_file_size=None):
    """Comprehensive security validation for patches."""
    
    issues = []
    allowed_paths = allowed_paths or []
    max_file_size = max_file_size or 10 * 1024 * 1024  # 10MB default
    
    for i, patch_obj in enumerate(patchset):
        target_path = patch_obj.target.decode('utf-8', errors='replace')
        
        # Check for absolute paths
        if xisabs(patch_obj.target):
            issues.append(f"Patch {i}: Absolute path not allowed: {target_path}")
        
        # Check for directory traversal
        normalized = xnormpath(patch_obj.target).decode('utf-8', errors='replace')
        if '..' in normalized or normalized.startswith('/'):
            issues.append(f"Patch {i}: Directory traversal detected: {target_path}")
        
        # Check against allowed paths
        if allowed_paths:
            allowed = any(normalized.startswith(allowed) for allowed in allowed_paths)
            if not allowed:
                issues.append(f"Patch {i}: Path not in allowed list: {target_path}")
        
        # Check file size limits
        if os.path.exists(target_path):
            file_size = os.path.getsize(target_path)
            if file_size > max_file_size:
                issues.append(f"Patch {i}: Target file too large: {target_path} ({file_size} bytes)")
        
        # Check for suspicious content
        for hunk in patch_obj.hunks:
            for line in hunk.text:
                line_str = line.decode('utf-8', errors='replace')
                
                # Check for potential code injection
                suspicious_patterns = [
                    'eval(', 'exec(', '__import__', 'subprocess',
                    'os.system', 'shell=True'
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in line_str and line_str.startswith('+'):
                        issues.append(f"Patch {i}: Suspicious code pattern: {pattern}")
    
    return issues

# Usage
patchset = patch.fromfile('untrusted.patch')
if patchset:
    security_issues = security_validate_patchset(
        patchset,
        allowed_paths=['src/', 'docs/', 'tests/'],
        max_file_size=1024 * 1024  # 1MB limit
    )
    
    if security_issues:
        print("Security validation failed:")
        for issue in security_issues:
            print(f"  - {issue}")
    else:
        print("Security validation passed")
        patchset.apply()
```

## Next Steps

- Review [Error Handling](error-handling.md) for robust error management
- Explore [Integration Examples](../examples/integration.md) for real-world scenarios
- Check [CLI Guide](cli.md) for command-line advanced usage
- See [API Reference](../api/index.md) for complete function documentation
