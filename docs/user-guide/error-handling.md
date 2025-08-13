# Error Handling

Robust error handling is crucial when working with patches, as they can fail for various reasons. This guide covers common error scenarios and best practices for handling them gracefully.

## Common Error Types

### 1. Parse Errors

Parse errors occur when the patch format is invalid or corrupted.

```python
import patch

def handle_parse_errors(patch_file):
    """Handle various parse error scenarios."""
    
    try:
        patchset = patch.fromfile(patch_file)
        
        if not patchset:
            print("❌ Failed to parse patch file")
            return None
        
        # Check for parsing issues
        if patchset.errors > 0:
            print(f"⚠️  {patchset.errors} parsing errors encountered")
            
            # Decide whether to proceed
            if patchset.errors > 5:  # Too many errors
                print("Too many parsing errors - aborting")
                return None
        
        if patchset.warnings > 0:
            print(f"⚠️  {patchset.warnings} parsing warnings")
        
        return patchset
        
    except FileNotFoundError:
        print(f"❌ Patch file not found: {patch_file}")
        return None
    except PermissionError:
        print(f"❌ Permission denied reading: {patch_file}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error parsing patch: {e}")
        return None

# Usage
patchset = handle_parse_errors('problematic.patch')
if patchset:
    print("✅ Patch parsed successfully")
```

### 2. Application Errors

Application errors happen when patches can't be applied to the target files.

```python
import patch
import os

def handle_application_errors(patchset, **options):
    """Handle patch application errors with detailed feedback."""
    
    if not patchset:
        return False
    
    # Pre-application checks
    print("🔍 Performing pre-application checks...")
    
    missing_files = []
    readonly_files = []
    strip = options.get('strip', 0)
    
    for p in patchset:
        target = p.target.decode('utf-8', errors='replace')
        
        # Apply strip logic
        if strip > 0:
            parts = target.split('/')
            if len(parts) > strip:
                target = '/'.join(parts[strip:])
        
        # Check if file exists
        if not os.path.exists(target):
            missing_files.append(target)
            continue
        
        # Check if file is writable
        if not os.access(target, os.W_OK):
            readonly_files.append(target)
    
    # Report issues
    if missing_files:
        print(f"❌ Missing target files:")
        for f in missing_files:
            print(f"   - {f}")
    
    if readonly_files:
        print(f"❌ Read-only target files:")
        for f in readonly_files:
            print(f"   - {f}")
    
    if missing_files or readonly_files:
        if not options.get('force', False):
            return False
        else:
            print("⚠️  Proceeding anyway due to --force option")
    
    # Dry run first
    print("🧪 Testing patch application...")
    try:
        dry_success = patchset.apply(dry_run=True, **options)
        
        if not dry_success:
            print("❌ Dry run failed - patches would not apply cleanly")
            
            # Try to provide more specific error information
            print("🔍 Analyzing potential conflicts...")
            analyze_conflicts(patchset, **options)
            return False
        
        print("✅ Dry run successful")
        
    except Exception as e:
        print(f"❌ Error during dry run: {e}")
        return False
    
    # Apply for real
    print("🚀 Applying patches...")
    try:
        success = patchset.apply(**options)
        
        if success:
            print("✅ All patches applied successfully!")
            return True
        else:
            print("❌ Some patches failed to apply")
            return False
            
    except Exception as e:
        print(f"❌ Error during patch application: {e}")
        return False

def analyze_conflicts(patchset, **options):
    """Analyze why patches might fail to apply."""
    
    strip = options.get('strip', 0)
    
    for i, p in enumerate(patchset):
        target = p.target.decode('utf-8', errors='replace')
        
        # Apply strip logic
        if strip > 0:
            parts = target.split('/')
            if len(parts) > strip:
                target = '/'.join(parts[strip:])
        
        print(f"File {i+1}: {target}")
        
        if not os.path.exists(target):
            print(f"   ❌ File does not exist")
            continue
        
        # Check each hunk
        try:
            with open(target, 'rb') as f:
                file_lines = f.readlines()
            
            for j, hunk in enumerate(p.hunks):
                print(f"   Hunk {j+1}: @@ -{hunk.startsrc},{hunk.linessrc} +{hunk.starttgt},{hunk.linestgt} @@")
                
                # Check if hunk can be applied
                if hunk.startsrc > len(file_lines):
                    print(f"      ❌ Start line {hunk.startsrc} beyond file end ({len(file_lines)} lines)")
                    continue
                
                # Check context lines
                context_matches = True
                for line_num, hunk_line in enumerate(hunk.text):
                    if hunk_line.startswith(b' ') or hunk_line.startswith(b'-'):
                        # This is a context or deletion line
                        file_line_idx = hunk.startsrc - 1 + line_num
                        if file_line_idx < len(file_lines):
                            expected = hunk_line[1:]  # Remove +/- prefix
                            actual = file_lines[file_line_idx].rstrip(b'\r\n')
                            if expected.rstrip(b'\r\n') != actual:
                                print(f"      ❌ Context mismatch at line {file_line_idx + 1}")
                                print(f"         Expected: {expected}")
                                print(f"         Actual:   {actual}")
                                context_matches = False
                                break
                
                if context_matches:
                    print(f"      ✅ Context matches")
                
        except Exception as e:
            print(f"   ❌ Error analyzing file: {e}")

# Usage
patchset = patch.fromfile('conflicting.patch')
if patchset:
    success = handle_application_errors(patchset, strip=1)
```

### 3. Network Errors (for URL patches)

```python
import patch
from urllib.error import URLError, HTTPError
import socket

def handle_url_patch(url, timeout=30):
    """Handle network-related errors when downloading patches."""
    
    # Set socket timeout
    socket.setdefaulttimeout(timeout)
    
    try:
        print(f"🌐 Downloading patch from: {url}")
        patchset = patch.fromurl(url)
        
        if not patchset:
            print("❌ Failed to parse downloaded patch")
            return None
        
        print(f"✅ Downloaded and parsed {len(patchset)} patches")
        return patchset
        
    except HTTPError as e:
        if e.code == 404:
            print(f"❌ Patch not found (404): {url}")
        elif e.code == 403:
            print(f"❌ Access forbidden (403): {url}")
        elif e.code >= 500:
            print(f"❌ Server error ({e.code}): {url}")
        else:
            print(f"❌ HTTP error ({e.code}): {e.reason}")
        return None
        
    except URLError as e:
        print(f"❌ URL error: {e.reason}")
        return None
        
    except socket.timeout:
        print(f"❌ Download timed out after {timeout} seconds")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error downloading patch: {e}")
        return None
    
    finally:
        # Reset timeout
        socket.setdefaulttimeout(None)

# Usage with retry logic
def download_with_retry(url, max_retries=3):
    """Download patch with retry logic."""
    
    for attempt in range(max_retries):
        print(f"Attempt {attempt + 1}/{max_retries}")
        
        patchset = handle_url_patch(url)
        if patchset:
            return patchset
        
        if attempt < max_retries - 1:
            print("Retrying in 5 seconds...")
            import time
            time.sleep(5)
    
    print("❌ All download attempts failed")
    return None

# Usage
patchset = download_with_retry('https://github.com/user/repo/commit/abc123.patch')
```

## Error Recovery Strategies

### 1. Backup and Restore

```python
import patch
import shutil
import tempfile
import os

class PatchBackup:
    """Context manager for patch operations with automatic backup/restore."""
    
    def __init__(self, patchset, strip=0):
        self.patchset = patchset
        self.strip = strip
        self.backup_dir = None
        self.backed_up_files = []
    
    def __enter__(self):
        # Create backup directory
        self.backup_dir = tempfile.mkdtemp(prefix='patch_backup_')
        
        # Backup all target files
        for p in self.patchset:
            target = p.target.decode('utf-8', errors='replace')
            
            # Apply strip logic
            if self.strip > 0:
                parts = target.split('/')
                if len(parts) > self.strip:
                    target = '/'.join(parts[self.strip:])
            
            if os.path.exists(target):
                backup_name = target.replace('/', '_').replace('\\', '_')
                backup_path = os.path.join(self.backup_dir, backup_name)
                
                shutil.copy2(target, backup_path)
                self.backed_up_files.append((target, backup_path))
                print(f"📁 Backed up: {target}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # An error occurred - restore from backup
            print("❌ Error occurred - restoring from backup...")
            self.restore()
        else:
            # Success - clean up backup
            print("✅ Operation successful - cleaning up backup...")
            self.cleanup()
    
    def restore(self):
        """Restore files from backup."""
        for original_path, backup_path in self.backed_up_files:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, original_path)
                print(f"🔄 Restored: {original_path}")
        self.cleanup()
    
    def cleanup(self):
        """Clean up backup directory."""
        if self.backup_dir and os.path.exists(self.backup_dir):
            shutil.rmtree(self.backup_dir)

# Usage
def safe_patch_apply(patch_file, **options):
    """Apply patch with automatic backup/restore on failure."""
    
    patchset = patch.fromfile(patch_file)
    if not patchset:
        return False
    
    try:
        with PatchBackup(patchset, options.get('strip', 0)):
            success = patchset.apply(**options)
            
            if not success:
                raise RuntimeError("Patch application failed")
            
            return True
            
    except Exception as e:
        print(f"❌ Patch application failed: {e}")
        return False

# Usage
safe_patch_apply('risky.patch', strip=1)
```

### 2. Partial Application Recovery

```python
import patch

def apply_with_partial_recovery(patchset, **options):
    """Apply patches one by one with recovery options."""
    
    applied_patches = []
    failed_patches = []
    
    for i, patch_obj in enumerate(patchset):
        target = patch_obj.target.decode('utf-8', errors='replace')
        print(f"📝 Applying patch {i+1}/{len(patchset)}: {target}")
        
        # Create temporary patchset with just this patch
        temp_patchset = patch.PatchSet()
        temp_patchset.items = [patch_obj]
        temp_patchset.type = patchset.type
        
        try:
            success = temp_patchset.apply(**options)
            
            if success:
                print(f"   ✅ Applied successfully")
                applied_patches.append((i, patch_obj))
            else:
                print(f"   ❌ Failed to apply")
                failed_patches.append((i, patch_obj))
                
                # Ask user what to do
                print(f"   Options:")
                print(f"   1. Continue with remaining patches")
                print(f"   2. Skip this patch and continue")
                print(f"   3. Abort and revert all changes")
                
                choice = input("   Choose (1/2/3): ").strip()
                
                if choice == '3':
                    print("🔄 Reverting all applied patches...")
                    revert_applied_patches(applied_patches, **options)
                    return False
                elif choice == '2':
                    print("⏭️  Skipping this patch")
                    continue
                # choice == '1' or default: continue
                
        except Exception as e:
            print(f"   ❌ Error applying patch: {e}")
            failed_patches.append((i, patch_obj))
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Applied: {len(applied_patches)}/{len(patchset)} patches")
    print(f"   Failed: {len(failed_patches)}/{len(patchset)} patches")
    
    if failed_patches:
        print(f"   Failed patches:")
        for i, patch_obj in failed_patches:
            target = patch_obj.target.decode('utf-8', errors='replace')
            print(f"     - {i+1}: {target}")
    
    return len(failed_patches) == 0

def revert_applied_patches(applied_patches, **options):
    """Revert a list of applied patches."""
    
    # Reverse the order for proper reversal
    for i, patch_obj in reversed(applied_patches):
        target = patch_obj.target.decode('utf-8', errors='replace')
        print(f"🔄 Reverting patch {i+1}: {target}")
        
        # Create temporary patchset for reversal
        temp_patchset = patch.PatchSet()
        temp_patchset.items = [patch_obj]
        temp_patchset.type = 'plain'
        
        try:
            success = temp_patchset.revert(**options)
            if success:
                print(f"   ✅ Reverted successfully")
            else:
                print(f"   ❌ Failed to revert")
        except Exception as e:
            print(f"   ❌ Error reverting patch: {e}")

# Usage
patchset = patch.fromfile('complex.patch')
if patchset:
    apply_with_partial_recovery(patchset, strip=1)
```

## Validation and Testing

### 1. Pre-application Validation

```python
import patch
import os

def validate_patch_application(patchset, **options):
    """Comprehensive validation before applying patches."""
    
    issues = []
    warnings = []
    
    # Basic validation
    if not patchset:
        issues.append("Invalid or empty patchset")
        return issues, warnings
    
    if patchset.errors > 0:
        issues.append(f"Parsing errors: {patchset.errors}")
    
    if patchset.warnings > 0:
        warnings.append(f"Parsing warnings: {patchset.warnings}")
    
    # File-level validation
    strip = options.get('strip', 0)
    root = options.get('root')
    
    for i, p in enumerate(patchset):
        target = p.target.decode('utf-8', errors='replace')
        
        # Apply strip logic
        if strip > 0:
            parts = target.split('/')
            if len(parts) > strip:
                target = '/'.join(parts[strip:])
        
        # Apply root directory
        if root:
            target = os.path.join(root, target)
        
        # Check file existence
        if not os.path.exists(target):
            issues.append(f"Missing target file: {target}")
            continue
        
        # Check file permissions
        if not os.access(target, os.R_OK):
            issues.append(f"Cannot read file: {target}")
        
        if not os.access(target, os.W_OK):
            issues.append(f"Cannot write to file: {target}")
        
        # Check file size (avoid huge files)
        try:
            file_size = os.path.getsize(target)
            if file_size > 100 * 1024 * 1024:  # 100MB
                warnings.append(f"Large file: {target} ({file_size} bytes)")
        except OSError:
            issues.append(f"Cannot access file: {target}")
    
    # Hunk-level validation
    for i, p in enumerate(patchset):
        for j, hunk in enumerate(p.hunks):
            if hunk.invalid:
                issues.append(f"Invalid hunk in patch {i+1}, hunk {j+1}")
            
            if hunk.startsrc <= 0 or hunk.starttgt <= 0:
                issues.append(f"Invalid line numbers in patch {i+1}, hunk {j+1}")
    
    return issues, warnings

def safe_apply_with_validation(patch_file, **options):
    """Apply patch with comprehensive validation."""
    
    # Parse patch
    patchset = patch.fromfile(patch_file)
    if not patchset:
        print("❌ Failed to parse patch file")
        return False
    
    # Validate
    print("🔍 Validating patch...")
    issues, warnings = validate_patch_application(patchset, **options)
    
    # Report issues
    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    if issues:
        print("❌ Validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        
        if not options.get('force', False):
            print("Use --force to apply anyway (not recommended)")
            return False
        else:
            print("⚠️  Proceeding anyway due to --force option")
    
    # Apply if validation passed
    print("✅ Validation passed - applying patch...")
    return patchset.apply(**options)

# Usage
safe_apply_with_validation('validated.patch', strip=1, force=False)
```

### 2. Post-application Testing

```python
import patch
import subprocess
import os

def apply_and_test(patch_file, test_commands, **options):
    """Apply patch and run tests to verify correctness."""
    
    # Apply the patch
    patchset = patch.fromfile(patch_file)
    if not patchset:
        return False
    
    print("🚀 Applying patch...")
    success = patchset.apply(**options)
    
    if not success:
        print("❌ Patch application failed")
        return False
    
    print("✅ Patch applied successfully")
    
    # Run tests
    all_tests_passed = True
    
    for i, test_cmd in enumerate(test_commands, 1):
        print(f"🧪 Running test {i}/{len(test_commands)}: {test_cmd}")
        
        try:
            result = subprocess.run(
                test_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"   ✅ Test passed")
            else:
                print(f"   ❌ Test failed (exit code: {result.returncode})")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                all_tests_passed = False
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Test timed out")
            all_tests_passed = False
        except Exception as e:
            print(f"   ❌ Error running test: {e}")
            all_tests_passed = False
    
    if all_tests_passed:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        
        # Offer to revert
        response = input("Revert patch due to test failures? (y/N): ")
        if response.lower().startswith('y'):
            print("🔄 Reverting patch...")
            revert_success = patchset.revert(**options)
            if revert_success:
                print("✅ Patch reverted successfully")
            else:
                print("❌ Failed to revert patch")
        
        return False

# Usage
test_commands = [
    'python -m pytest tests/',
    'python -m flake8 src/',
    'python -m mypy src/'
]

apply_and_test('feature.patch', test_commands, strip=1)
```

## Best Practices Summary

### 1. Always Validate Input

- Check return values from parsing functions
- Validate file existence and permissions
- Use dry run before actual application

### 2. Provide Clear Feedback

- Use descriptive error messages
- Show progress for long operations
- Offer recovery options when possible

### 3. Implement Graceful Degradation

- Continue with partial success when possible
- Offer manual intervention options
- Provide detailed failure analysis

### 4. Use Defensive Programming

- Handle all exception types appropriately
- Validate assumptions about file state
- Implement timeouts for network operations

### 5. Enable Recovery

- Create backups before risky operations
- Implement rollback mechanisms
- Provide clear recovery instructions

## Next Steps

- Review [Advanced Usage](advanced.md) for complex scenarios
- Check [Examples](../examples/basic.md) for practical implementations
- Explore the [API Reference](../api/index.md) for detailed function documentation
