# Utilities Module

The `patch.utils` module provides utility functions for cross-platform path handling and other common operations used throughout the library.

## Functions

::: patch.utils.xisabs
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.utils.xnormpath
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.utils.xstrip
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Usage Examples

### Cross-Platform Path Handling

```python
from patch.utils import xisabs, xnormpath, xstrip

# Check if path is absolute (works on all platforms)
print(xisabs(b'/usr/local/bin'))        # True (Unix)
print(xisabs(b'C:\\Windows\\System32'))  # True (Windows)
print(xisabs(b'relative/path'))         # False
print(xisabs(b'./current/dir'))         # False

# Normalize paths for consistent handling
path1 = xnormpath(b'a/b/../c/./d')      # b'a/c/d'
path2 = xnormpath(b'a\\b\\..\\c\\.\\d') # b'a/c/d' (Windows)
path3 = xnormpath(b'/a/b/c/../d')       # b'/a/b/d'

print(f"Normalized: {path1}")
print(f"Normalized: {path2}")
print(f"Normalized: {path3}")

# Strip leading path components
original = b'a/b/c/file.txt'
stripped1 = xstrip(original, 1)  # b'b/c/file.txt'
stripped2 = xstrip(original, 2)  # b'c/file.txt'
stripped3 = xstrip(original, 3)  # b'file.txt'

print(f"Original: {original}")
print(f"Strip 1: {stripped1}")
print(f"Strip 2: {stripped2}")
print(f"Strip 3: {stripped3}")
```

### Path Security Validation

```python
from patch.utils import xisabs, xnormpath

def validate_patch_path(path_bytes, allow_absolute=False):
    """Validate that a patch path is safe to use."""
    
    # Check for absolute paths (security risk)
    if xisabs(path_bytes) and not allow_absolute:
        raise ValueError(f"Absolute paths not allowed: {path_bytes}")
    
    # Normalize the path
    normalized = xnormpath(path_bytes)
    
    # Check for directory traversal attempts
    if b'..' in normalized.split(b'/'):
        raise ValueError(f"Directory traversal detected: {path_bytes}")
    
    # Check for null bytes (security)
    if b'\x00' in normalized:
        raise ValueError(f"Null byte in path: {path_bytes}")
    
    return normalized

# Usage in patch processing
def safe_patch_application(patchset, root_dir=None):
    """Apply patches with path validation."""
    
    for patch_obj in patchset:
        try:
            # Validate source and target paths
            safe_source = validate_patch_path(patch_obj.source)
            safe_target = validate_patch_path(patch_obj.target)
            
            print(f"Applying patch: {safe_source} -> {safe_target}")
            
            # Continue with application...
            
        except ValueError as e:
            print(f"Security error: {e}")
            return False
    
    return True
```

### Path Stripping Utilities

```python
from patch.utils import xstrip

def smart_strip_detection(patchset):
    """Automatically detect optimal strip level for a patchset."""
    
    # Collect all target paths
    paths = [patch_obj.target for patch_obj in patchset]
    
    # Try different strip levels
    for strip_level in range(5):  # Test 0-4
        valid_paths = 0
        
        for path in paths:
            stripped = xstrip(path, strip_level)
            
            # Check if stripped path would be valid
            if stripped and not xisabs(stripped):
                # Convert to string for file existence check
                path_str = stripped.decode('utf-8', errors='replace')
                if os.path.exists(path_str) or '/' not in path_str:
                    valid_paths += 1
        
        # If most paths are valid with this strip level, use it
        if valid_paths >= len(paths) * 0.8:  # 80% threshold
            return strip_level
    
    return 0  # Default to no stripping

# Usage
patchset = patch.fromfile('github-commit.patch')
if patchset:
    optimal_strip = smart_strip_detection(patchset)
    print(f"Recommended strip level: {optimal_strip}")
    
    success = patchset.apply(strip=optimal_strip)
    print(f"Application result: {success}")
```

### Path Conversion Utilities

```python
from patch.utils import xnormpath
import os

def convert_patch_paths(patchset, source_root, target_root):
    """Convert patch paths from one directory structure to another."""
    
    for patch_obj in patchset:
        # Normalize current paths
        source_path = xnormpath(patch_obj.source)
        target_path = xnormpath(patch_obj.target)
        
        # Convert bytes to string for path operations
        source_str = source_path.decode('utf-8', errors='replace')
        target_str = target_path.decode('utf-8', errors='replace')
        
        # Remove source root and add target root
        if source_str.startswith(source_root):
            rel_path = source_str[len(source_root):].lstrip('/')
            new_target = os.path.join(target_root, rel_path)
            
            # Update patch object
            patch_obj.target = new_target.encode('utf-8')
            
            print(f"Converted: {source_str} -> {new_target}")

# Usage
patchset = patch.fromfile('project-a.patch')
if patchset:
    convert_patch_paths(patchset, '/old/project', '/new/project')
    success = patchset.apply()
```

## Advanced Utilities

### Custom Path Handlers

```python
from patch.utils import xnormpath, xstrip

class PatchPathHandler:
    """Advanced path handling for complex patch scenarios."""
    
    def __init__(self, base_dir=None, strip_level=0, path_mapping=None):
        self.base_dir = base_dir
        self.strip_level = strip_level
        self.path_mapping = path_mapping or {}
    
    def resolve_path(self, patch_path_bytes):
        """Resolve a patch path to actual filesystem path."""
        
        # Normalize the path
        normalized = xnormpath(patch_path_bytes)
        
        # Apply stripping
        if self.strip_level > 0:
            normalized = xstrip(normalized, self.strip_level)
        
        # Convert to string
        path_str = normalized.decode('utf-8', errors='replace')
        
        # Apply path mapping
        for old_prefix, new_prefix in self.path_mapping.items():
            if path_str.startswith(old_prefix):
                path_str = new_prefix + path_str[len(old_prefix):]
                break
        
        # Apply base directory
        if self.base_dir:
            path_str = os.path.join(self.base_dir, path_str)
        
        return path_str
    
    def apply_to_patchset(self, patchset):
        """Apply path resolution to all patches in a patchset."""
        
        for patch_obj in patchset:
            # Resolve target path
            resolved_target = self.resolve_path(patch_obj.target)
            patch_obj.target = resolved_target.encode('utf-8')
            
            # Optionally resolve source path
            if patch_obj.source:
                resolved_source = self.resolve_path(patch_obj.source)
                patch_obj.source = resolved_source.encode('utf-8')

# Usage
handler = PatchPathHandler(
    base_dir='/project',
    strip_level=1,
    path_mapping={
        'old_module/': 'new_module/',
        'legacy/': 'modern/'
    }
)

patchset = patch.fromfile('migration.patch')
if patchset:
    handler.apply_to_patchset(patchset)
    success = patchset.apply()
```

### Path Validation Utilities

```python
from patch.utils import xisabs, xnormpath
import os

def validate_patch_security(patchset, allowed_dirs=None):
    """Validate patch paths for security concerns."""
    
    issues = []
    allowed_dirs = allowed_dirs or []
    
    for i, patch_obj in enumerate(patchset):
        target_path = xnormpath(patch_obj.target)
        target_str = target_path.decode('utf-8', errors='replace')
        
        # Check for absolute paths
        if xisabs(target_path):
            issues.append(f"Patch {i}: Absolute path detected: {target_str}")
        
        # Check for directory traversal
        if '..' in target_str:
            issues.append(f"Patch {i}: Directory traversal detected: {target_str}")
        
        # Check against allowed directories
        if allowed_dirs:
            allowed = any(target_str.startswith(allowed_dir) 
                         for allowed_dir in allowed_dirs)
            if not allowed:
                issues.append(f"Patch {i}: Path outside allowed directories: {target_str}")
        
        # Check for suspicious characters
        suspicious_chars = ['\x00', '\r', '\n']
        for char in suspicious_chars:
            if char in target_str:
                issues.append(f"Patch {i}: Suspicious character in path: {target_str}")
    
    return issues

# Usage
patchset = patch.fromfile('untrusted.patch')
if patchset:
    security_issues = validate_patch_security(
        patchset, 
        allowed_dirs=['src/', 'docs/', 'tests/']
    )
    
    if security_issues:
        print("Security issues detected:")
        for issue in security_issues:
            print(f"  - {issue}")
        print("Patch rejected for security reasons")
    else:
        print("Patch passed security validation")
        patchset.apply()
```

## Platform Compatibility

### Windows Path Handling

```python
from patch.utils import xnormpath

def windows_path_conversion(patch_path):
    """Convert Unix-style patch paths for Windows."""
    
    # Normalize path separators
    normalized = xnormpath(patch_path)
    
    # Convert to Windows format if needed
    if os.name == 'nt':
        path_str = normalized.decode('utf-8', errors='replace')
        windows_path = path_str.replace('/', '\\')
        return windows_path.encode('utf-8')
    
    return normalized

# Usage on Windows
if os.name == 'nt':
    for patch_obj in patchset:
        patch_obj.target = windows_path_conversion(patch_obj.target)
        if patch_obj.source:
            patch_obj.source = windows_path_conversion(patch_obj.source)
```

## Next Steps

- Explore [Core Classes](core.md) for patch data structures
- Learn about [Application Module](application.md) for patch operations
- See [Parser Module](parser.md) for parsing utilities
- Check [Examples](../examples/advanced.md) for complex scenarios
