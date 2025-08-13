# Advanced Examples

This section provides comprehensive examples for complex patch operations, integration scenarios, and advanced use cases.

## Complex Patch Scenarios

### Multi-Format Patch Handling

```python
import patch
from patch.parser import detect_type

def handle_mixed_format_patches(patch_files):
    """Handle patches from different version control systems."""
    
    results = {}
    
    for patch_file in patch_files:
        print(f"\nProcessing: {patch_file}")
        
        # Parse the patch
        patchset = patch.fromfile(patch_file)
        if not patchset:
            results[patch_file] = {'status': 'failed', 'reason': 'parse_error'}
            continue
        
        # Detect format for each patch in the set
        formats = set()
        for patch_obj in patchset:
            patch_format = detect_type(patch_obj)
            formats.add(patch_format)
        
        print(f"  Detected formats: {', '.join(formats)}")
        print(f"  Files affected: {len(patchset)}")
        print(f"  Total changes: +{sum(p.added for p in patchset)} -{sum(p.removed for p in patchset)}")
        
        # Apply with format-specific handling
        if 'git' in formats:
            # Git patches may need special handling for binary files
            success = apply_git_patches(patchset)
        elif 'svn' in formats:
            # SVN patches may have property changes
            success = apply_svn_patches(patchset)
        else:
            # Standard application for plain diffs
            success = patchset.apply(strip=1)
        
        results[patch_file] = {
            'status': 'success' if success else 'failed',
            'formats': list(formats),
            'file_count': len(patchset)
        }
    
    return results

def apply_git_patches(patchset):
    """Apply Git-format patches with special handling."""
    # Git patches might include binary files, renames, etc.
    return patchset.apply(strip=1)

def apply_svn_patches(patchset):
    """Apply SVN-format patches with property handling."""
    # SVN patches might include property changes
    return patchset.apply(strip=0)  # SVN often doesn't need stripping

# Usage
patch_files = [
    'git-commit.patch',
    'svn-diff.patch', 
    'plain-diff.patch'
]

results = handle_mixed_format_patches(patch_files)
for file, result in results.items():
    print(f"{file}: {result['status']}")
```

### Large-Scale Patch Operations

```python
import patch
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BatchPatchProcessor:
    """Process large numbers of patches efficiently."""
    
    def __init__(self, max_workers=4, backup_dir=None):
        self.max_workers = max_workers
        self.backup_dir = backup_dir
        self.results = []
    
    def process_patch_file(self, patch_file):
        """Process a single patch file."""
        try:
            logger.info(f"Processing {patch_file}")
            
            # Parse patch
            patchset = patch.fromfile(patch_file)
            if not patchset:
                return {
                    'file': patch_file,
                    'status': 'failed',
                    'reason': 'parse_error',
                    'files_affected': 0
                }
            
            # Create backups if requested
            if self.backup_dir:
                self._create_backups(patchset, patch_file)
            
            # Apply patches
            success = patchset.apply()
            
            return {
                'file': patch_file,
                'status': 'success' if success else 'failed',
                'reason': 'applied' if success else 'application_error',
                'files_affected': len(patchset),
                'changes': f"+{sum(p.added for p in patchset)} -{sum(p.removed for p in patchset)}"
            }
            
        except Exception as e:
            logger.error(f"Error processing {patch_file}: {e}")
            return {
                'file': patch_file,
                'status': 'failed',
                'reason': str(e),
                'files_affected': 0
            }
    
    def _create_backups(self, patchset, patch_file):
        """Create backups for affected files."""
        backup_subdir = os.path.join(self.backup_dir, os.path.basename(patch_file))
        os.makedirs(backup_subdir, exist_ok=True)
        
        for patch_obj in patchset:
            target_file = patch_obj.target.decode('utf-8')
            if os.path.exists(target_file):
                backup_file = os.path.join(backup_subdir, os.path.basename(target_file))
                shutil.copy2(target_file, backup_file)
    
    def process_directory(self, patch_dir, pattern="*.patch"):
        """Process all patches in a directory."""
        
        # Find all patch files
        patch_files = glob.glob(os.path.join(patch_dir, pattern))
        patch_files.extend(glob.glob(os.path.join(patch_dir, "*.diff")))
        
        if not patch_files:
            logger.warning(f"No patch files found in {patch_dir}")
            return []
        
        logger.info(f"Found {len(patch_files)} patch files")
        
        # Process in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all jobs
            future_to_file = {
                executor.submit(self.process_patch_file, pf): pf 
                for pf in patch_files
            }
            
            # Collect results
            for future in as_completed(future_to_file):
                result = future.result()
                self.results.append(result)
                
                status_icon = "✓" if result['status'] == 'success' else "✗"
                logger.info(f"{status_icon} {result['file']}: {result['reason']}")
        
        return self.results
    
    def generate_report(self):
        """Generate a summary report of all operations."""
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'success')
        failed = total - successful
        
        total_files = sum(r['files_affected'] for r in self.results)
        
        print(f"\n{'='*60}")
        print(f"BATCH PATCH PROCESSING REPORT")
        print(f"{'='*60}")
        print(f"Total patches processed: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Files affected: {total_files}")
        print(f"Success rate: {(successful/total*100):.1f}%")
        
        if failed > 0:
            print(f"\nFailed patches:")
            for result in self.results:
                if result['status'] == 'failed':
                    print(f"  - {result['file']}: {result['reason']}")

# Usage
processor = BatchPatchProcessor(max_workers=8, backup_dir='backups/')
results = processor.process_directory('incoming_patches/')
processor.generate_report()
```

### Intelligent Conflict Resolution

```python
import patch
import difflib
import os

class ConflictResolver:
    """Automatically resolve simple patch conflicts."""
    
    def __init__(self, strategy='conservative'):
        self.strategy = strategy
        self.resolved_conflicts = 0
    
    def resolve_conflicts(self, patchset):
        """Attempt to resolve conflicts in a patchset."""
        
        for patch_obj in patchset:
            target_file = patch_obj.target.decode('utf-8')
            
            if not os.path.exists(target_file):
                continue
            
            # Read current file content
            with open(target_file, 'rb') as f:
                current_lines = f.readlines()
            
            # Try to resolve each hunk
            for hunk in patch_obj.hunks:
                if self._has_conflict(hunk, current_lines):
                    resolved = self._resolve_hunk_conflict(hunk, current_lines)
                    if resolved:
                        self.resolved_conflicts += 1
                        logger.info(f"Resolved conflict in {target_file}")
    
    def _has_conflict(self, hunk, current_lines):
        """Check if a hunk would conflict with current file."""
        try:
            # Simple check: see if context lines match
            start_line = hunk.startsrc - 1  # Convert to 0-based
            
            if start_line >= len(current_lines):
                return True
            
            # Check context lines
            hunk_context = [line for line in hunk.text if line.startswith(b' ')]
            file_context = current_lines[start_line:start_line + len(hunk_context)]
            
            return hunk_context != file_context
            
        except (IndexError, AttributeError):
            return True
    
    def _resolve_hunk_conflict(self, hunk, current_lines):
        """Attempt to resolve a single hunk conflict."""
        
        if self.strategy == 'conservative':
            # Only resolve if we can find exact match nearby
            return self._conservative_resolve(hunk, current_lines)
        elif self.strategy == 'fuzzy':
            # Use fuzzy matching to find best location
            return self._fuzzy_resolve(hunk, current_lines)
        
        return False
    
    def _conservative_resolve(self, hunk, current_lines):
        """Conservative conflict resolution."""
        # Look for exact context match within ±5 lines
        context_lines = [line for line in hunk.text if line.startswith(b' ')]
        
        if not context_lines:
            return False
        
        original_start = hunk.startsrc - 1
        
        # Search nearby lines
        for offset in range(-5, 6):
            test_start = original_start + offset
            
            if test_start < 0 or test_start + len(context_lines) > len(current_lines):
                continue
            
            test_context = current_lines[test_start:test_start + len(context_lines)]
            
            if test_context == context_lines:
                # Found exact match - update hunk position
                hunk.startsrc = test_start + 1
                hunk.starttgt = test_start + 1
                return True
        
        return False
    
    def _fuzzy_resolve(self, hunk, current_lines):
        """Fuzzy conflict resolution using difflib."""
        context_lines = [line.decode('utf-8', errors='replace') 
                        for line in hunk.text if line.startswith(b' ')]
        
        if not context_lines:
            return False
        
        # Convert current file to strings
        current_strings = [line.decode('utf-8', errors='replace') 
                          for line in current_lines]
        
        # Find best match using sequence matcher
        matcher = difflib.SequenceMatcher(None, context_lines, current_strings)
        match = matcher.find_longest_match(0, len(context_lines), 
                                         0, len(current_strings))
        
        if match.size >= len(context_lines) * 0.8:  # 80% match threshold
            # Update hunk position
            hunk.startsrc = match.b + 1
            hunk.starttgt = match.b + 1
            return True
        
        return False

# Usage
patchset = patch.fromfile('conflicting.patch')
if patchset:
    resolver = ConflictResolver(strategy='conservative')
    resolver.resolve_conflicts(patchset)
    
    print(f"Resolved {resolver.resolved_conflicts} conflicts")
    
    success = patchset.apply()
    if success:
        print("Patches applied successfully after conflict resolution")
    else:
        print("Some conflicts could not be resolved automatically")
```

## Performance Benchmarking

### Patch Performance Analysis

```python
import patch
import time
import psutil
import os

class PatchPerformanceAnalyzer:
    """Analyze patch performance characteristics."""
    
    def __init__(self):
        self.metrics = {}
    
    def benchmark_patch_operation(self, patch_file, operation='apply'):
        """Benchmark a specific patch operation."""
        
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Start timing
        start_time = time.time()
        
        try:
            # Parse patch
            parse_start = time.time()
            patchset = patch.fromfile(patch_file)
            parse_time = time.time() - parse_start
            
            if not patchset:
                return None
            
            # Perform operation
            op_start = time.time()
            
            if operation == 'apply':
                success = patchset.apply()
            elif operation == 'diffstat':
                success = bool(patchset.diffstat())
            elif operation == 'parse_only':
                success = True
            else:
                raise ValueError(f"Unknown operation: {operation}")
            
            op_time = time.time() - op_start
            total_time = time.time() - start_time
            
            # Get final memory usage
            final_memory = process.memory_info().rss
            memory_delta = final_memory - initial_memory
            
            # Collect metrics
            metrics = {
                'patch_file': patch_file,
                'operation': operation,
                'success': success,
                'total_time': total_time,
                'parse_time': parse_time,
                'operation_time': op_time,
                'memory_delta': memory_delta,
                'file_count': len(patchset),
                'total_changes': sum(p.added + p.removed for p in patchset),
                'patch_size': os.path.getsize(patch_file)
            }
            
            return metrics
            
        except Exception as e:
            return {
                'patch_file': patch_file,
                'operation': operation,
                'success': False,
                'error': str(e),
                'total_time': time.time() - start_time
            }
    
    def benchmark_multiple_patches(self, patch_files, operations=None):
        """Benchmark multiple patches and operations."""
        
        operations = operations or ['parse_only', 'diffstat', 'apply']
        
        for patch_file in patch_files:
            for operation in operations:
                metrics = self.benchmark_patch_operation(patch_file, operation)
                
                if metrics:
                    key = f"{patch_file}_{operation}"
                    self.metrics[key] = metrics
                    
                    if metrics['success']:
                        print(f"✓ {patch_file} ({operation}): {metrics['total_time']:.3f}s")
                    else:
                        print(f"✗ {patch_file} ({operation}): {metrics.get('error', 'failed')}")
    
    def generate_performance_report(self):
        """Generate detailed performance report."""
        
        if not self.metrics:
            print("No metrics collected")
            return
        
        print(f"\n{'='*80}")
        print(f"PERFORMANCE ANALYSIS REPORT")
        print(f"{'='*80}")
        
        # Group by operation
        by_operation = {}
        for key, metrics in self.metrics.items():
            op = metrics['operation']
            if op not in by_operation:
                by_operation[op] = []
            by_operation[op].append(metrics)
        
        for operation, metrics_list in by_operation.items():
            successful = [m for m in metrics_list if m['success']]
            
            if not successful:
                continue
            
            print(f"\n{operation.upper()} OPERATION:")
            print(f"  Successful operations: {len(successful)}/{len(metrics_list)}")
            
            # Time statistics
            times = [m['total_time'] for m in successful]
            print(f"  Average time: {sum(times)/len(times):.3f}s")
            print(f"  Min time: {min(times):.3f}s")
            print(f"  Max time: {max(times):.3f}s")
            
            # Memory statistics
            memory_deltas = [m.get('memory_delta', 0) for m in successful]
            avg_memory = sum(memory_deltas) / len(memory_deltas)
            print(f"  Average memory delta: {avg_memory/1024/1024:.2f} MB")
            
            # Throughput statistics
            if operation == 'apply':
                changes = [m['total_changes'] for m in successful]
                avg_changes = sum(changes) / len(changes)
                avg_time = sum(times) / len(times)
                throughput = avg_changes / avg_time if avg_time > 0 else 0
                print(f"  Average throughput: {throughput:.1f} changes/second")

# Usage
analyzer = PatchPerformanceAnalyzer()

# Benchmark a set of patches
patch_files = glob.glob('benchmarks/*.patch')
analyzer.benchmark_multiple_patches(patch_files)
analyzer.generate_performance_report()
```

### Patch Validation and Testing

```python
import patch
import tempfile
import subprocess
import shutil

class PatchValidator:
    """Comprehensive patch validation system."""
    
    def __init__(self, test_commands=None):
        self.test_commands = test_commands or []
        self.validation_results = {}
    
    def validate_patch(self, patch_file, target_dir='.'):
        """Validate a patch through multiple checks."""
        
        results = {
            'patch_file': patch_file,
            'syntax_valid': False,
            'applies_cleanly': False,
            'tests_pass': False,
            'no_conflicts': False,
            'details': {}
        }
        
        try:
            # 1. Syntax validation
            patchset = patch.fromfile(patch_file)
            if patchset:
                results['syntax_valid'] = True
                results['details']['file_count'] = len(patchset)
                results['details']['total_changes'] = sum(p.added + p.removed for p in patchset)
            else:
                results['details']['syntax_error'] = 'Failed to parse patch'
                return results
            
            # 2. Application test in isolated environment
            with tempfile.TemporaryDirectory() as test_dir:
                # Copy target directory
                test_target = os.path.join(test_dir, 'target')
                shutil.copytree(target_dir, test_target)
                
                # Try to apply patch
                test_success = patchset.apply(root=test_target)
                results['applies_cleanly'] = test_success
                
                if not test_success:
                    results['details']['application_error'] = 'Patch does not apply cleanly'
                    return results
                
                # 3. Run tests if specified
                if self.test_commands:
                    test_results = self._run_tests(test_target)
                    results['tests_pass'] = test_results['success']
                    results['details']['test_output'] = test_results['output']
                else:
                    results['tests_pass'] = True  # No tests to run
                
                # 4. Check for conflicts with existing changes
                conflict_check = self._check_conflicts(patchset, target_dir)
                results['no_conflicts'] = conflict_check['clean']
                results['details']['conflicts'] = conflict_check['conflicts']
        
        except Exception as e:
            results['details']['validation_error'] = str(e)
        
        return results
    
    def _run_tests(self, test_dir):
        """Run test commands in the test directory."""
        
        for command in self.test_commands:
            try:
                result = subprocess.run(
                    command,
                    cwd=test_dir,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode != 0:
                    return {
                        'success': False,
                        'output': result.stderr,
                        'command': ' '.join(command)
                    }
            
            except subprocess.TimeoutExpired:
                return {
                    'success': False,
                    'output': 'Test command timed out',
                    'command': ' '.join(command)
                }
            except Exception as e:
                return {
                    'success': False,
                    'output': str(e),
                    'command': ' '.join(command)
                }
        
        return {'success': True, 'output': 'All tests passed'}
    
    def _check_conflicts(self, patchset, target_dir):
        """Check for potential conflicts with uncommitted changes."""
        
        conflicts = []
        
        # Check if we're in a git repository
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=target_dir,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                # There are uncommitted changes
                modified_files = set()
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        status = line[:2]
                        filename = line[3:]
                        if 'M' in status:  # Modified files
                            modified_files.add(filename)
                
                # Check if patch affects modified files
                for patch_obj in patchset:
                    target_file = patch_obj.target.decode('utf-8')
                    if target_file in modified_files:
                        conflicts.append(f"Patch affects modified file: {target_file}")
        
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Not a git repository or git not available
            pass
        
        return {
            'clean': len(conflicts) == 0,
            'conflicts': conflicts
        }
    
    def validate_multiple(self, patch_files, target_dir='.'):
        """Validate multiple patches."""
        
        for patch_file in patch_files:
            result = self.validate_patch(patch_file, target_dir)
            self.validation_results[patch_file] = result
        
        return self.validation_results
    
    def print_validation_report(self):
        """Print comprehensive validation report."""
        
        print(f"\n{'='*80}")
        print(f"PATCH VALIDATION REPORT")
        print(f"{'='*80}")
        
        total = len(self.validation_results)
        fully_valid = 0
        
        for patch_file, results in self.validation_results.items():
            print(f"\n{patch_file}:")
            
            checks = [
                ('Syntax Valid', results['syntax_valid']),
                ('Applies Cleanly', results['applies_cleanly']),
                ('Tests Pass', results['tests_pass']),
                ('No Conflicts', results['no_conflicts'])
            ]
            
            all_passed = all(passed for _, passed in checks)
            if all_passed:
                fully_valid += 1
            
            for check_name, passed in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {check_name}")
            
            # Show details for failures
            if not all_passed and 'details' in results:
                for key, value in results['details'].items():
                    if 'error' in key.lower() or 'conflict' in key.lower():
                        print(f"    - {key}: {value}")
        
        print(f"\nSummary: {fully_valid}/{total} patches fully validated")
        return fully_valid == total

# Usage
validator = PatchValidator(test_commands=[
    ['python', '-m', 'pytest', 'tests/', '-x'],
    ['python', '-m', 'flake8', 'src/']
])

patch_files = ['feature-1.patch', 'bugfix-2.patch', 'refactor-3.patch']
validator.validate_multiple(patch_files)
all_valid = validator.print_validation_report()

if all_valid:
    print("All patches validated - safe to apply")
else:
    print("Some patches failed validation")
```

## Next Steps

- Explore [Integration Examples](integration.md) for real-world scenarios
- Review [Basic Examples](basic.md) for simpler use cases
- Check [API Reference](../api/index.md) for complete documentation
- See [User Guide](../user-guide/advanced.md) for additional advanced techniques
