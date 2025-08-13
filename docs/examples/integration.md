# Integration Examples

This section demonstrates how to integrate Python Patch with various tools, frameworks, and workflows commonly used in software development.

## CI/CD Integration

### GitHub Actions Integration

```yaml
# .github/workflows/apply-patches.yml
name: Apply Patches

on:
  push:
    paths:
      - 'patches/**'
  workflow_dispatch:
    inputs:
      patch_file:
        description: 'Specific patch file to apply'
        required: false

jobs:
  apply-patches:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        pip install python-patch
        
    - name: Apply patches
      run: |
        #!/bin/bash
        set -e
        
        if [ -n "${{ github.event.inputs.patch_file }}" ]; then
          # Apply specific patch
          echo "Applying specific patch: ${{ github.event.inputs.patch_file }}"
          python -m patch -p1 "${{ github.event.inputs.patch_file }}"
        else
          # Apply all patches in patches/ directory
          for patch in patches/*.patch; do
            if [ -f "$patch" ]; then
              echo "Applying $patch"
              python -m patch -p1 "$patch"
            fi
          done
        fi
        
    - name: Run tests
      run: |
        python -m pytest tests/ -v
        
    - name: Commit changes
      if: success()
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add -A
        git diff --staged --quiet || git commit -m "Applied patches via GitHub Actions"
        git push
```

### Jenkins Pipeline Integration

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    environment {
        PATCH_DIR = 'patches'
        TARGET_DIR = 'src'
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                sh 'pip install python-patch'
            }
        }
        
        stage('Validate Patches') {
            steps {
                script {
                    def patchFiles = sh(
                        script: "find ${PATCH_DIR} -name '*.patch' -o -name '*.diff'",
                        returnStdout: true
                    ).trim().split('\n')
                    
                    for (patchFile in patchFiles) {
                        if (patchFile) {
                            echo "Validating ${patchFile}"
                            sh "python -m patch --diffstat '${patchFile}'"
                        }
                    }
                }
            }
        }
        
        stage('Apply Patches') {
            steps {
                script {
                    def patchFiles = sh(
                        script: "find ${PATCH_DIR} -name '*.patch' -o -name '*.diff' | sort",
                        returnStdout: true
                    ).trim().split('\n')
                    
                    for (patchFile in patchFiles) {
                        if (patchFile) {
                            echo "Applying ${patchFile}"
                            sh "python -m patch -p1 '${patchFile}'"
                        }
                    }
                }
            }
        }
        
        stage('Test') {
            steps {
                sh 'python -m pytest tests/ --junitxml=test-results.xml'
            }
            post {
                always {
                    junit 'test-results.xml'
                }
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'logs/*.log', allowEmptyArchive: true
            }
        }
    }
    
    post {
        failure {
            emailext (
                subject: "Patch Application Failed: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Patch application failed. Check console output for details.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
```

### Docker Integration

```dockerfile
# Multi-stage Dockerfile with patch application
FROM python:3.9-slim as base

# Install python-patch
RUN pip install python-patch

# Copy source code
COPY src/ /app/src/
COPY patches/ /app/patches/

WORKDIR /app

# Apply patches stage
FROM base as patched

# Apply all patches
RUN for patch in patches/*.patch; do \
        echo "Applying $patch"; \
        python -m patch -p1 "$patch" || exit 1; \
    done

# Verify patches applied correctly
RUN python -c "import src; print('Patches applied successfully')"

# Production stage
FROM patched as production

# Install production dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Set up application
COPY . .
EXPOSE 8000

CMD ["python", "-m", "src.main"]
```

## Web Framework Integration

### Flask Integration

```python
from flask import Flask, request, jsonify, send_file
import patch
import tempfile
import os
import zipfile

app = Flask(__name__)

@app.route('/api/patch/apply', methods=['POST'])
def apply_patch_api():
    """API endpoint for applying patches."""
    
    try:
        # Get patch content from request
        if 'patch_file' in request.files:
            patch_content = request.files['patch_file'].read()
        elif 'patch_content' in request.json:
            patch_content = request.json['patch_content'].encode('utf-8')
        else:
            return jsonify({'error': 'No patch content provided'}), 400
        
        # Parse patch
        patchset = patch.fromstring(patch_content)
        if not patchset:
            return jsonify({'error': 'Invalid patch format'}), 400
        
        # Get options
        options = request.json.get('options', {}) if request.json else {}
        strip_level = options.get('strip', 1)
        dry_run = options.get('dry_run', False)
        
        # Apply patch
        if dry_run:
            # Just return what would be changed
            diffstat_output = patchset.diffstat()
            return jsonify({
                'success': True,
                'dry_run': True,
                'changes': diffstat_output,
                'files_affected': len(patchset)
            })
        else:
            success = patchset.apply(strip=strip_level)
            
            return jsonify({
                'success': success,
                'files_affected': len(patchset),
                'changes_applied': sum(p.added + p.removed for p in patchset)
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/patch/validate', methods=['POST'])
def validate_patch_api():
    """API endpoint for validating patches."""
    
    try:
        patch_content = request.files['patch_file'].read()
        
        # Parse and validate
        patchset = patch.fromstring(patch_content)
        
        if not patchset:
            return jsonify({
                'valid': False,
                'errors': ['Failed to parse patch']
            })
        
        # Collect validation info
        validation_info = {
            'valid': True,
            'file_count': len(patchset),
            'total_additions': sum(p.added for p in patchset),
            'total_deletions': sum(p.removed for p in patchset),
            'errors': patchset.errors,
            'warnings': patchset.warnings,
            'files': []
        }
        
        for patch_obj in patchset:
            file_info = {
                'target': patch_obj.target.decode('utf-8', errors='replace'),
                'additions': patch_obj.added,
                'deletions': patch_obj.removed,
                'hunks': len(patch_obj.hunks)
            }
            validation_info['files'].append(file_info)
        
        return jsonify(validation_info)
    
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [str(e)]
        }), 500

@app.route('/api/patch/diffstat', methods=['POST'])
def diffstat_api():
    """API endpoint for generating diffstat."""
    
    try:
        patch_content = request.files['patch_file'].read()
        patchset = patch.fromstring(patch_content)
        
        if not patchset:
            return jsonify({'error': 'Invalid patch'}), 400
        
        diffstat_output = patchset.diffstat()
        
        return jsonify({
            'diffstat': diffstat_output,
            'summary': {
                'files': len(patchset),
                'insertions': sum(p.added for p in patchset),
                'deletions': sum(p.removed for p in patchset)
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Integration

```python
# Django views.py
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import patch
import json

@csrf_exempt
@require_http_methods(["POST"])
def apply_patch_view(request):
    """Django view for patch application."""
    
    try:
        # Handle file upload or JSON content
        if request.FILES.get('patch_file'):
            patch_content = request.FILES['patch_file'].read()
        else:
            data = json.loads(request.body)
            patch_content = data['patch_content'].encode('utf-8')
        
        # Parse and apply
        patchset = patch.fromstring(patch_content)
        if not patchset:
            return JsonResponse({'error': 'Invalid patch format'}, status=400)
        
        # Apply with Django settings
        from django.conf import settings
        project_root = getattr(settings, 'PROJECT_ROOT', '.')
        
        success = patchset.apply(root=project_root, strip=1)
        
        return JsonResponse({
            'success': success,
            'files_affected': len(patchset),
            'message': 'Patch applied successfully' if success else 'Patch application failed'
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Django management command
# management/commands/apply_patches.py
from django.core.management.base import BaseCommand
from django.conf import settings
import patch
import glob
import os

class Command(BaseCommand):
    help = 'Apply patches from the patches directory'
    
    def add_arguments(self, parser):
        parser.add_argument('--patch-dir', default='patches',
                          help='Directory containing patch files')
        parser.add_argument('--strip', type=int, default=1,
                          help='Strip level for patch paths')
        parser.add_argument('--dry-run', action='store_true',
                          help='Show what would be changed without applying')
    
    def handle(self, *args, **options):
        patch_dir = options['patch_dir']
        strip_level = options['strip']
        dry_run = options['dry_run']
        
        # Find patch files
        patch_files = glob.glob(os.path.join(patch_dir, '*.patch'))
        
        if not patch_files:
            self.stdout.write(f"No patch files found in {patch_dir}")
            return
        
        self.stdout.write(f"Found {len(patch_files)} patch files")
        
        for patch_file in sorted(patch_files):
            self.stdout.write(f"Processing {patch_file}...")
            
            patchset = patch.fromfile(patch_file)
            if not patchset:
                self.stderr.write(f"Failed to parse {patch_file}")
                continue
            
            if dry_run:
                self.stdout.write(f"Would affect {len(patchset)} files:")
                self.stdout.write(patchset.diffstat())
            else:
                success = patchset.apply(strip=strip_level)
                if success:
                    self.stdout.write(f"✓ Applied {patch_file}")
                else:
                    self.stderr.write(f"✗ Failed to apply {patch_file}")

# Usage: python manage.py apply_patches --dry-run
```

## Database Integration

### Patch Metadata Storage

```python
import patch
import sqlite3
import json
from datetime import datetime

class PatchDatabase:
    """Store and manage patch metadata in SQLite."""
    
    def __init__(self, db_path='patches.db'):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the database schema."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    applied_at TIMESTAMP,
                    status TEXT NOT NULL,
                    file_count INTEGER,
                    additions INTEGER,
                    deletions INTEGER,
                    diffstat TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS patch_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patch_id INTEGER,
                    target_file TEXT NOT NULL,
                    additions INTEGER,
                    deletions INTEGER,
                    hunks INTEGER,
                    FOREIGN KEY (patch_id) REFERENCES patches (id)
                )
            ''')
    
    def record_patch_application(self, patch_file, patchset, success):
        """Record patch application in database."""
        
        with sqlite3.connect(self.db_path) as conn:
            # Insert main patch record
            cursor = conn.execute('''
                INSERT INTO patches (
                    filename, applied_at, status, file_count, 
                    additions, deletions, diffstat, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patch_file,
                datetime.now(),
                'applied' if success else 'failed',
                len(patchset),
                sum(p.added for p in patchset),
                sum(p.removed for p in patchset),
                patchset.diffstat(),
                json.dumps({
                    'type': patchset.type,
                    'errors': patchset.errors,
                    'warnings': patchset.warnings
                })
            ))
            
            patch_id = cursor.lastrowid
            
            # Insert file records
            for patch_obj in patchset:
                conn.execute('''
                    INSERT INTO patch_files (
                        patch_id, target_file, additions, deletions, hunks
                    ) VALUES (?, ?, ?, ?, ?)
                ''', (
                    patch_id,
                    patch_obj.target.decode('utf-8', errors='replace'),
                    patch_obj.added,
                    patch_obj.removed,
                    len(patch_obj.hunks)
                ))
    
    def get_patch_history(self, limit=50):
        """Get recent patch application history."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT * FROM patches 
                ORDER BY applied_at DESC 
                LIMIT ?
            ''', (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_file_patch_history(self, filename):
        """Get patch history for a specific file."""
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT p.filename, p.applied_at, p.status, 
                       pf.additions, pf.deletions, pf.hunks
                FROM patches p
                JOIN patch_files pf ON p.id = pf.patch_id
                WHERE pf.target_file = ?
                ORDER BY p.applied_at DESC
            ''', (filename,))
            
            return [dict(row) for row in cursor.fetchall()]

# Usage with database tracking
def apply_patch_with_tracking(patch_file):
    """Apply patch and record in database."""
    
    db = PatchDatabase()
    
    # Parse patch
    patchset = patch.fromfile(patch_file)
    if not patchset:
        print(f"Failed to parse {patch_file}")
        return False
    
    # Apply patch
    success = patchset.apply(strip=1)
    
    # Record in database
    db.record_patch_application(patch_file, patchset, success)
    
    if success:
        print(f"✓ Applied {patch_file} (recorded in database)")
    else:
        print(f"✗ Failed to apply {patch_file} (failure recorded)")
    
    return success

# Query patch history
db = PatchDatabase()
history = db.get_patch_history(10)
for record in history:
    print(f"{record['applied_at']}: {record['filename']} ({record['status']})")
```

## Testing Framework Integration

### Pytest Integration

```python
# conftest.py
import pytest
import patch
import tempfile
import shutil
import os

@pytest.fixture
def patch_test_environment():
    """Create isolated environment for patch testing."""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        test_files = {
            'src/main.py': '''def hello():
    print("Hello World")
    return True
''',
            'tests/test_main.py': '''import sys
sys.path.insert(0, '../src')
from main import hello

def test_hello():
    assert hello() == True
''',
            'README.md': '''# Test Project

This is a test project for patch validation.
'''
        }
        
        # Create directory structure and files
        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
        
        yield temp_dir

@pytest.fixture
def sample_patch():
    """Provide a sample patch for testing."""
    
    return '''--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,3 @@
 def hello():
-    print("Hello World")
+    print("Hello Python Patch!")
     return True
'''

# test_patch_integration.py
import pytest
import patch
import os

class TestPatchIntegration:
    """Integration tests for patch operations."""
    
    def test_patch_application_workflow(self, patch_test_environment, sample_patch):
        """Test complete patch application workflow."""
        
        # Change to test environment
        original_cwd = os.getcwd()
        os.chdir(patch_test_environment)
        
        try:
            # Parse patch
            patchset = patch.fromstring(sample_patch)
            assert patchset is not False
            assert len(patchset) == 1
            
            # Verify target file exists
            target_file = 'src/main.py'
            assert os.path.exists(target_file)
            
            # Apply patch
            success = patchset.apply()
            assert success is True
            
            # Verify changes
            with open(target_file, 'r') as f:
                content = f.read()
            
            assert 'Hello Python Patch!' in content
            assert 'Hello World' not in content
            
        finally:
            os.chdir(original_cwd)
    
    def test_patch_validation_before_application(self, patch_test_environment):
        """Test patch validation workflow."""
        
        os.chdir(patch_test_environment)
        
        try:
            # Create a conflicting patch
            conflicting_patch = '''--- a/src/main.py
+++ b/src/main.py
@@ -1,3 +1,3 @@
 def hello():
-    print("Nonexistent line")
+    print("This will conflict")
     return True
'''
            
            patchset = patch.fromstring(conflicting_patch)
            assert patchset is not False
            
            # This should fail due to conflict
            success = patchset.apply()
            assert success is False
            
        finally:
            os.chdir(original_cwd)

# Run with: pytest test_patch_integration.py -v
```

### Unittest Integration

```python
import unittest
import patch
import tempfile
import os
import shutil

class PatchTestCase(unittest.TestCase):
    """Base test case for patch operations."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create test files
        self._create_test_files()
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """Create standard test files."""
        
        test_content = {
            'file1.txt': 'line1\nline2\nline3\n',
            'file2.txt': 'content1\ncontent2\ncontent3\n'
        }
        
        for filename, content in test_content.items():
            with open(filename, 'w') as f:
                f.write(content)
    
    def assertPatchApplies(self, patch_content, strip=0):
        """Assert that a patch applies successfully."""
        
        patchset = patch.fromstring(patch_content)
        self.assertIsNotFalse(patchset, "Patch should parse successfully")
        
        success = patchset.apply(strip=strip)
        self.assertTrue(success, "Patch should apply successfully")
        
        return patchset
    
    def assertPatchFails(self, patch_content, strip=0):
        """Assert that a patch fails to apply."""
        
        patchset = patch.fromstring(patch_content)
        
        if patchset is not False:
            success = patchset.apply(strip=strip)
            self.assertFalse(success, "Patch should fail to apply")
        
        return patchset

class TestPatchOperations(PatchTestCase):
    """Test various patch operations."""
    
    def test_simple_patch_application(self):
        """Test basic patch application."""
        
        patch_content = '''--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,3 @@
 line1
-line2
+modified line2
 line3
'''
        
        patchset = self.assertPatchApplies(patch_content)
        
        # Verify changes
        with open('file1.txt', 'r') as f:
            content = f.read()
        
        self.assertIn('modified line2', content)
        self.assertNotIn('line2\n', content)
    
    def test_patch_revert(self):
        """Test patch reversal."""
        
        patch_content = '''--- a/file1.txt
+++ b/file1.txt
@@ -1,3 +1,3 @@
 line1
-line2
+modified line2
 line3
'''
        
        # Apply patch
        patchset = self.assertPatchApplies(patch_content)
        
        # Revert patch
        success = patchset.revert()
        self.assertTrue(success, "Patch should revert successfully")
        
        # Verify original content restored
        with open('file1.txt', 'r') as f:
            content = f.read()
        
        self.assertIn('line2', content)
        self.assertNotIn('modified line2', content)

if __name__ == '__main__':
    unittest.main()
```

## Monitoring and Logging

### Comprehensive Logging

```python
import patch
import logging
import sys
from datetime import datetime

# Configure detailed logging
def setup_patch_logging(log_file='patch_operations.log'):
    """Set up comprehensive logging for patch operations."""
    
    # Create logger
    logger = logging.getLogger('patch_operations')
    logger.setLevel(logging.DEBUG)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler for detailed logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler for important messages
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def logged_patch_application(patch_file, **kwargs):
    """Apply patch with comprehensive logging."""
    
    logger = logging.getLogger('patch_operations')
    
    logger.info(f"Starting patch application: {patch_file}")
    logger.debug(f"Application options: {kwargs}")
    
    try:
        # Parse patch
        logger.debug("Parsing patch file...")
        patchset = patch.fromfile(patch_file)
        
        if not patchset:
            logger.error("Failed to parse patch file")
            return False
        
        logger.info(f"Parsed {len(patchset)} file patches")
        logger.debug(f"Parse errors: {patchset.errors}, warnings: {patchset.warnings}")
        
        # Log patch details
        for i, patch_obj in enumerate(patchset):
            target = patch_obj.target.decode('utf-8', errors='replace')
            logger.debug(f"Patch {i+1}: {target} (+{patch_obj.added} -{patch_obj.removed})")
        
        # Generate diffstat
        diffstat_output = patchset.diffstat()
        logger.info(f"Changes preview:\n{diffstat_output}")
        
        # Apply patches
        logger.info("Applying patches...")
        success = patchset.apply(**kwargs)
        
        if success:
            logger.info("All patches applied successfully")
        else:
            logger.error("Some patches failed to apply")
        
        return success
        
    except Exception as e:
        logger.exception(f"Error during patch application: {e}")
        return False

# Usage
logger = setup_patch_logging()
success = logged_patch_application('feature.patch', strip=1, dry_run=False)
```

### Metrics Collection

```python
import patch
import time
import psutil
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class PatchMetrics:
    """Metrics for patch operations."""
    
    patch_file: str
    operation: str
    success: bool
    duration: float
    memory_peak: int
    file_count: int
    total_changes: int
    patch_size: int
    error_message: str = None

class PatchMetricsCollector:
    """Collect and analyze patch operation metrics."""
    
    def __init__(self):
        self.metrics: List[PatchMetrics] = []
        self.process = psutil.Process()
    
    def measure_operation(self, patch_file, operation_func, *args, **kwargs):
        """Measure a patch operation and collect metrics."""
        
        # Initial measurements
        start_time = time.time()
        initial_memory = self.process.memory_info().rss
        patch_size = os.path.getsize(patch_file)
        
        peak_memory = initial_memory
        success = False
        error_message = None
        file_count = 0
        total_changes = 0
        
        try:
            # Monitor memory during operation
            def memory_monitor():
                nonlocal peak_memory
                current_memory = self.process.memory_info().rss
                peak_memory = max(peak_memory, current_memory)
            
            # Execute operation
            result = operation_func(patch_file, *args, **kwargs)
            memory_monitor()
            
            # Extract metrics from result
            if isinstance(result, tuple):
                success, patchset = result
                if patchset:
                    file_count = len(patchset)
                    total_changes = sum(p.added + p.removed for p in patchset)
            else:
                success = bool(result)
                if result and hasattr(result, '__len__'):
                    file_count = len(result)
                    if hasattr(result, 'items'):
                        total_changes = sum(p.added + p.removed for p in result)
            
        except Exception as e:
            error_message = str(e)
            memory_monitor()
        
        # Calculate final metrics
        duration = time.time() - start_time
        memory_delta = peak_memory - initial_memory
        
        # Create metrics record
        metrics = PatchMetrics(
            patch_file=patch_file,
            operation=operation_func.__name__,
            success=success,
            duration=duration,
            memory_peak=memory_delta,
            file_count=file_count,
            total_changes=total_changes,
            patch_size=patch_size,
            error_message=error_message
        )
        
        self.metrics.append(metrics)
        return metrics
    
    def generate_metrics_report(self):
        """Generate comprehensive metrics report."""
        
        if not self.metrics:
            print("No metrics collected")
            return
        
        print(f"\n{'='*80}")
        print(f"PATCH OPERATIONS METRICS REPORT")
        print(f"{'='*80}")
        
        # Overall statistics
        total_ops = len(self.metrics)
        successful_ops = sum(1 for m in self.metrics if m.success)
        
        print(f"Total operations: {total_ops}")
        print(f"Successful: {successful_ops} ({successful_ops/total_ops*100:.1f}%)")
        print(f"Failed: {total_ops - successful_ops}")
        
        # Performance statistics
        successful_metrics = [m for m in self.metrics if m.success]
        
        if successful_metrics:
            durations = [m.duration for m in successful_metrics]
            memory_peaks = [m.memory_peak for m in successful_metrics]
            
            print(f"\nPerformance Statistics:")
            print(f"  Average duration: {sum(durations)/len(durations):.3f}s")
            print(f"  Min duration: {min(durations):.3f}s")
            print(f"  Max duration: {max(durations):.3f}s")
            print(f"  Average memory delta: {sum(memory_peaks)/len(memory_peaks)/1024/1024:.2f} MB")
            
            # Throughput analysis
            total_changes = sum(m.total_changes for m in successful_metrics)
            total_time = sum(durations)
            if total_time > 0:
                throughput = total_changes / total_time
                print(f"  Overall throughput: {throughput:.1f} changes/second")
        
        # Error analysis
        failed_metrics = [m for m in self.metrics if not m.success]
        if failed_metrics:
            print(f"\nFailure Analysis:")
            error_counts = {}
            for m in failed_metrics:
                error = m.error_message or 'Unknown error'
                error_counts[error] = error_counts.get(error, 0) + 1
            
            for error, count in error_counts.items():
                print(f"  {error}: {count} occurrences")

# Usage functions for metrics collection
def measured_patch_apply(patch_file):
    """Apply patch and return success status with patchset."""
    patchset = patch.fromfile(patch_file)
    if patchset:
        success = patchset.apply(strip=1)
        return success, patchset
    return False, None

def measured_patch_validate(patch_file):
    """Validate patch and return status with patchset."""
    patchset = patch.fromfile(patch_file)
    if patchset:
        # Just parsing is validation
        return True, patchset
    return False, None

# Usage
collector = PatchMetricsCollector()

# Measure various operations
patch_files = ['patch1.patch', 'patch2.patch', 'patch3.patch']

for patch_file in patch_files:
    # Measure validation
    collector.measure_operation(patch_file, measured_patch_validate)
    
    # Measure application
    collector.measure_operation(patch_file, measured_patch_apply)

# Generate report
collector.generate_metrics_report()
```

## Next Steps

- Review [Basic Examples](basic.md) for simpler use cases
- Explore [User Guide](../user-guide/advanced.md) for advanced techniques
- Check [API Reference](../api/index.md) for complete documentation
- See [Development Guide](../development/testing.md) for testing best practices
