# Development Scripts

This directory contains utility scripts for development and testing.

## Scripts

### run_debug.py / run_debug.bat

Launch the GUI with comprehensive debug logging enabled.

**Usage:**
```bash
# Windows
scripts\run_debug.bat

# Or directly with Python
python scripts/run_debug.py
```

**Purpose**: Helps troubleshoot GUI issues by showing detailed logs.

### capture_screenshots.py

Automated screenshot capture for documentation.

**Usage:**
```bash
python scripts/capture_screenshots.py
```

**Purpose**: Captures screenshots of different GUI panels for README documentation.

**Note**: For best results, capture screenshots manually while connected to a real oscilloscope (see `docs/SCREENSHOT_GUIDE.md`).

## Development Workflow

These scripts are not installed with the package - they're for development only.

For package development documentation, see:
- `docs/development/BUILD.md` - Build and packaging instructions
- `docs/development/PYPI_DEPLOYMENT.md` - PyPI deployment guide
- `docs/CONTRIBUTING.md` - Contributing guidelines
