# Parser Module

The `patch.parser` module contains the core parsing logic for analyzing unified diff patches and detecting their format types. It provides utilities for stream processing and patch format detection.

## Functions

::: patch.parser.detect_type
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

::: patch.parser.normalize_filenames
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Classes

::: patch.parser.wrapumerate
    options:
      show_source: true
      show_root_heading: true
      show_root_full_path: false
      heading_level: 2

## Usage Examples

### Patch Type Detection

```python
from patch.parser import detect_type
from patch.core import Patch

# Create a patch object (normally done by parsing)
patch_obj = Patch()
patch_obj.header = [b"diff --git a/file.txt b/file.txt"]

# Detect the patch type
patch_type = detect_type(patch_obj)
print(f"Patch type: {patch_type}")  # Output: git
```

### Stream Enumeration

```python
from patch.parser import wrapumerate
from io import BytesIO

# Create a sample stream
content = b"line1\nline2\nline3\n"
stream = BytesIO(content)

# Wrap the stream for parsing
wrapper = wrapumerate(stream)

# Process each line
while wrapper.next():
    print(f"Line {wrapper.lineno}: {wrapper.line.strip()}")
    
    # Check if we've reached the end
    if wrapper.is_empty:
        break
```

### Filename Normalization

```python
from patch.parser import normalize_filenames
from patch.core import Patch

# Create a patch with various filename formats
patch_obj = Patch()
patch_obj.source = b"a/src/file.py"
patch_obj.target = b"b/src/file.py"

# Normalize the filenames
normalize_filenames(patch_obj)

print(f"Source: {patch_obj.source}")  # Normalized path
print(f"Target: {patch_obj.target}")  # Normalized path
```

## Patch Format Types

The parser can detect several patch formats:

### Git Format
- Contains `diff --git` headers
- May include `index` lines with object hashes
- Supports binary patches and renames

```
diff --git a/file.txt b/file.txt
index 1234567..abcdefg 100644
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
```

### SVN Format
- Contains `Index:` headers
- Uses `===` separators
- May include property changes

```
Index: file.txt
===================================================================
--- file.txt	(revision 123)
+++ file.txt	(working copy)
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
```

### Mercurial Format
- Contains `diff -r` headers with revision hashes
- May include changeset information
- Supports both plain and Git-style formats

```
diff -r 1234567890ab file.txt
--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
```

### Plain Format
- Standard unified diff format
- No version control specific headers
- Simple `---` and `+++` filename lines

```
--- file.txt.orig
+++ file.txt
@@ -1,3 +1,3 @@
 line1
-old line
+new line
 line3
```

## Advanced Parsing

### Custom Stream Processing

```python
from patch.parser import wrapumerate
from io import BytesIO

def parse_custom_format(content):
    """Example of custom parsing using wrapumerate."""
    stream = BytesIO(content)
    wrapper = wrapumerate(stream)
    
    headers = []
    hunks = []
    
    # Parse headers
    while wrapper.next():
        line = wrapper.line
        
        if line.startswith(b"@@"):
            # Found hunk header, break to process hunks
            break
        elif line.startswith(b"---") or line.startswith(b"+++"):
            headers.append(line)
    
    # Parse hunks
    current_hunk = []
    while wrapper.next():
        line = wrapper.line
        
        if line.startswith(b"@@"):
            if current_hunk:
                hunks.append(current_hunk)
                current_hunk = []
        
        current_hunk.append(line)
    
    if current_hunk:
        hunks.append(current_hunk)
    
    return headers, hunks
```

### Error Handling in Parsing

```python
from patch.parser import detect_type
from patch.core import Patch

def safe_type_detection(patch_obj):
    """Safely detect patch type with fallback."""
    try:
        patch_type = detect_type(patch_obj)
        
        if patch_type in ['git', 'svn', 'hg']:
            print(f"Detected {patch_type.upper()} format")
        else:
            print("Using plain diff format")
        
        return patch_type
        
    except Exception as e:
        print(f"Type detection failed: {e}")
        return 'plain'  # Safe fallback
```

## Performance Considerations

### Memory Usage
- `wrapumerate` processes streams line-by-line to minimize memory usage
- Large patches are handled efficiently without loading entire content
- Stream-based approach allows processing of patches larger than available RAM

### Parsing Speed
- Type detection is optimized to check most common formats first
- Filename normalization uses efficient regex patterns
- Early termination when format is definitively identified

## Next Steps

- Learn about [Application Methods](application.md) for applying parsed patches
- Explore [Core Classes](core.md) for working with parsed data
- See [Utilities](utils.md) for path handling functions
- Check [Examples](../examples/advanced.md) for complex parsing scenarios
