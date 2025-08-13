# Python Patch Documentation

This directory contains the comprehensive documentation for Python Patch, built with MkDocs and the Material theme.

## 📁 Directory Structure

```
docs/
├── README.md                    # This file
├── index.md                     # Main documentation homepage
├── getting-started/             # Getting started guides
│   ├── installation.md          # Installation instructions
│   ├── quick-start.md           # Quick start tutorial
│   └── basic-usage.md           # Basic usage patterns
├── user-guide/                  # Comprehensive user guides
│   ├── cli.md                   # Command-line interface guide
│   ├── api.md                   # Python API guide
│   ├── advanced.md              # Advanced usage patterns
│   └── error-handling.md        # Error handling strategies
├── api/                         # API reference documentation
│   ├── index.md                 # API overview
│   ├── api.md                   # Main API functions
│   ├── core.md                  # Core classes
│   ├── parser.md                # Parser module
│   ├── application.md           # Application module
│   ├── cli.md                   # CLI module
│   └── utils.md                 # Utility functions
├── examples/                    # Practical examples
│   ├── basic.md                 # Basic usage examples
│   ├── advanced.md              # Advanced examples
│   └── integration.md           # Integration examples
├── development/                 # Development documentation
│   ├── contributing.md          # Contributing guidelines
│   ├── setup.md                 # Development setup
│   ├── testing.md               # Testing guide
│   └── release.md               # Release process
├── about/                       # Project information
│   ├── changelog.md             # Version history
│   ├── license.md               # License information
│   └── credits.md               # Contributors and credits
├── stylesheets/                 # Custom CSS
│   └── extra.css                # Additional styling
└── javascripts/                 # Custom JavaScript
    └── mathjax.js               # MathJax configuration
```

## 🚀 Building the Documentation

### Prerequisites

Install the required dependencies:

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Or install individual packages
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Local Development

To serve the documentation locally for development:

```bash
# Start the development server
mkdocs serve

# The documentation will be available at http://127.0.0.1:8000
```

### Building for Production

To build the static documentation:

```bash
# Build the documentation
mkdocs build

# Output will be in the site/ directory
```

## 📝 Writing Documentation

### Markdown Guidelines

- Use clear, descriptive headings
- Include code examples with proper syntax highlighting
- Use admonitions for important notes, warnings, and tips
- Cross-reference related sections using relative links

### Code Examples

Use fenced code blocks with language specification:

````markdown
```python
import patch

patchset = patch.fromfile('example.patch')
if patchset:
    patchset.apply(strip=1)
```
````

### Admonitions

Use Material theme admonitions for special content:

```markdown
!!! note "Important Note"
    This is an important note that readers should pay attention to.

!!! warning "Warning"
    This is a warning about potential issues.

!!! tip "Pro Tip"
    This is a helpful tip for advanced users.
```

### API Documentation

API documentation is automatically generated from docstrings using mkdocstrings:

```markdown
::: patch.fromfile
    options:
      show_source: true
      show_root_heading: true
```

## 🎨 Styling and Themes

### Material Theme Configuration

The documentation uses the Material theme with:

- Light/dark mode toggle
- Navigation tabs and sections
- Search functionality
- Code copy buttons
- Git integration for edit links

### Custom Styling

Additional styling is provided in `stylesheets/extra.css`:

- Enhanced code block styling
- Custom admonition colors
- Improved table formatting
- Responsive design improvements

## 🔧 Configuration

### MkDocs Configuration

The main configuration is in `mkdocs.yml` at the project root:

- Site metadata and URLs
- Theme configuration and features
- Plugin configuration
- Navigation structure
- Markdown extensions

### Key Plugins

- **mkdocstrings**: Automatic API documentation from docstrings
- **git-revision-date-localized**: Last modified dates
- **git-committers**: Contributor information
- **minify**: HTML/CSS/JS minification

## 🚀 Deployment

### GitHub Pages

Documentation is automatically deployed to GitHub Pages via GitHub Actions:

1. **Trigger**: Push to main branch or manual workflow dispatch
2. **Build**: MkDocs builds the static site
3. **Deploy**: Site is deployed to GitHub Pages
4. **URL**: <https://astroair.github.io/python-patch/>

### Workflow

The deployment workflow (`.github/workflows/docs.yml`) includes:

- Documentation building and validation
- Link checking
- Quality assurance checks
- Automatic deployment on success

## 📋 Content Guidelines

### Writing Style

- **Clear and Concise**: Use simple, direct language
- **User-Focused**: Write from the user's perspective
- **Example-Rich**: Include practical examples
- **Progressive**: Start simple, build complexity

### Structure

- **Logical Flow**: Organize content logically
- **Cross-References**: Link related sections
- **Consistent Format**: Use consistent formatting
- **Complete Coverage**: Cover all features and use cases

### Maintenance

- **Keep Updated**: Update docs with code changes
- **Fix Broken Links**: Regular link checking
- **User Feedback**: Incorporate user suggestions
- **Version Sync**: Keep docs in sync with releases

## 🤝 Contributing to Documentation

### How to Contribute

1. **Fork** the repository
2. **Create** a documentation branch
3. **Make** your changes
4. **Test** locally with `mkdocs serve`
5. **Submit** a pull request

### What to Contribute

- **Fix Errors**: Typos, broken links, outdated information
- **Add Examples**: Real-world usage examples
- **Improve Clarity**: Better explanations and organization
- **Add Content**: Missing features or use cases

### Review Process

Documentation changes go through the same review process as code:

1. **Automated Checks**: Link validation, build verification
2. **Peer Review**: Review by maintainers
3. **Testing**: Verify changes work correctly
4. **Deployment**: Automatic deployment after merge

## 📞 Support

### Getting Help

- **GitHub Issues**: Report documentation bugs or request improvements
- **GitHub Discussions**: Ask questions about usage
- **Email**: Contact maintainers directly

### Feedback

We welcome feedback on documentation:

- **Clarity**: Is something confusing?
- **Completeness**: Is something missing?
- **Accuracy**: Is something incorrect?
- **Usability**: Is something hard to find?

---

**Happy documenting!** 📚✨
