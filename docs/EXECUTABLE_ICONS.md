# Executable Icon Configuration

This document describes how the application icons are configured for different platforms when building standalone executables with PyInstaller.

## Updated Icon Files

All PyInstaller spec files have been updated to use the new "Test Equipment" icon set:

- **Windows**: `resources/Test Equipment.ico` (17 KB)
- **macOS**: `resources/Test Equipment.icns` (703 KB)
- **Linux**: `resources/Test Equipment.png` (777 KB)

## Configured Executables

### 1. Siglent GUI Application (`siglent-gui.spec`)

**File**: `siglent-gui.spec`

**Icons Configured**:
- Windows: `resources/Test Equipment.ico`
- macOS: `resources/Test Equipment.icns` (for .app bundle)
- Linux: No icon embedded (Linux doesn't support icons in executables)

**Build Commands**:
```bash
# Windows
pyinstaller siglent-gui.spec

# macOS
pyinstaller siglent-gui.spec

# Linux
pyinstaller siglent-gui.spec
```

**Output**:
- Windows: `dist/SiglentGUI.exe` with embedded icon
- macOS: `dist/SiglentGUI.app` with icon in bundle
- Linux: `dist/SiglentGUI` (no embedded icon)

---

### 2. Report Generator - Windows (`report-generator-windows.spec`)

**File**: `report-generator-windows.spec`

**Icons Configured**:
- Windows: `resources/Test Equipment.ico`

**Build Command**:
```bash
pyinstaller report-generator-windows.spec
```

**Output**:
- `dist/SiglentReportGenerator/SiglentReportGenerator.exe` with embedded icon

**Icon Locations**:
- Line 125: Main executable icon
- Line 162: One-file executable variant (commented out)

---

### 3. Report Generator - Linux (`report-generator-linux.spec`)

**File**: `report-generator-linux.spec`

**Icons Configured**:
- PNG icon bundled in resources for AppImage/desktop integration
- Icon copied to AppDir for Linux desktop entries

**Build Command**:
```bash
pyinstaller report-generator-linux.spec
```

**Output**:
- `dist/SiglentReportGenerator/SiglentReportGenerator` (no embedded icon)
- Icon bundled at `resources/Test Equipment.png` for desktop integration

**AppImage Integration**:
The commented AppImage section (lines 137-177) includes:
- Icon copy to AppDir root: `shutil.copy('resources/Test Equipment.png', appdir / 'siglent-report-generator.png')`
- Desktop entry with icon reference: `Icon=siglent-report-generator`

---

## Icon File Requirements

### Windows (.ico)
- **Format**: ICO (Windows Icon)
- **Sizes**: Multiple resolutions (16x16, 32x32, 48x48, 256x256 recommended)
- **Current File**: `resources/Test Equipment.ico` (17 KB)
- **Used By**: PyInstaller EXE on Windows

### macOS (.icns)
- **Format**: ICNS (Apple Icon Image)
- **Sizes**: Multiple resolutions up to 1024x1024
- **Current File**: `resources/Test Equipment.icns` (703 KB)
- **Used By**: PyInstaller .app bundle on macOS
- **Requirements**: Must contain at least 512x512@2x for Retina displays

### Linux (.png)
- **Format**: PNG
- **Recommended Size**: 256x256 or 512x512
- **Current File**: `resources/Test Equipment.png` (777 KB)
- **Used By**: Desktop files, AppImage, window managers

---

## Testing the Icons

### Windows
1. Build the executable:
   ```bash
   pyinstaller siglent-gui.spec
   # or
   pyinstaller report-generator-windows.spec
   ```

2. Check the icon:
   - View `dist/` folder in File Explorer
   - The .exe should show the "Test Equipment" icon
   - Right-click → Properties → check icon in dialog
   - Run the .exe and check taskbar icon

### macOS
1. Build the application:
   ```bash
   pyinstaller siglent-gui.spec
   ```

2. Check the icon:
   - Open `dist/` folder in Finder
   - The .app bundle should show the "Test Equipment" icon
   - Right-click → Get Info → check icon preview
   - Run the app and check Dock icon

### Linux
1. Build the executable:
   ```bash
   pyinstaller siglent-gui.spec
   # or
   pyinstaller report-generator-linux.spec
   ```

2. For desktop integration:
   - Create a .desktop file in `~/.local/share/applications/`
   - Set `Icon=/path/to/resources/Test Equipment.png`
   - The application will use this icon in launchers and menus

---

## Troubleshooting

### Icon Not Appearing on Windows

**Problem**: .exe shows default Python icon instead of custom icon

**Solutions**:
1. Verify icon file exists: `ls resources/Test\ Equipment.ico`
2. Rebuild with verbose output: `pyinstaller --clean siglent-gui.spec`
3. Check spec file has correct icon path
4. Ensure icon file is valid ICO format (not just renamed PNG)

### Icon Not Appearing on macOS

**Problem**: .app bundle shows generic document icon

**Solutions**:
1. Verify ICNS file exists: `ls resources/Test\ Equipment.icns`
2. Rebuild with: `pyinstaller --clean siglent-gui.spec`
3. Clear icon cache: `sudo rm -rf /Library/Caches/com.apple.iconservices.store`
4. Restart Finder: `killall Finder`
5. Ensure ICNS has required resolutions (512x512@2x minimum)

### AppImage Icon Not Appearing on Linux

**Problem**: AppImage doesn't show icon in launcher

**Solutions**:
1. Verify PNG is copied to AppDir root
2. Check desktop file has correct Icon= entry
3. Ensure icon filename matches (no spaces or special chars)
4. Update desktop database: `update-desktop-database ~/.local/share/applications/`

---

## Icon in Application Code (PyQt6)

To use the icon within the running application (window title bar, about dialogs, etc.):

```python
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
import sys
from pathlib import Path

app = QApplication(sys.argv)

# Get icon path (works in both dev and bundled executable)
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    base_path = Path(sys._MEIPASS)
else:
    # Running in development
    base_path = Path(__file__).parent.parent

# Set application icon
icon_path = base_path / 'resources' / 'Test Equipment.ico'
if icon_path.exists():
    app.setWindowIcon(QIcon(str(icon_path)))

# Or set on specific window
from PyQt6.QtWidgets import QMainWindow
window = QMainWindow()
window.setWindowIcon(QIcon(str(icon_path)))
```

**Note**: For bundled executables, you must include the icon in `datas` in the spec file:

```python
datas=[
    ('resources/Test Equipment.ico', 'resources'),
    ('resources/Test Equipment.png', 'resources'),
],
```

---

## Build Automation

The icons are automatically configured when using the Makefile:

```bash
# Build GUI for current platform
make build-exe

# Build report generator for Windows
make build-report-generator-windows

# Build report generator for Linux
make build-report-generator-linux
```

All build targets automatically use the correct icon for the target platform.

---

## Related Files

- `siglent-gui.spec` - GUI application build configuration
- `report-generator-windows.spec` - Windows report generator build
- `report-generator-linux.spec` - Linux report generator build
- `resources/Test Equipment.ico` - Windows icon
- `resources/Test Equipment.icns` - macOS icon
- `resources/Test Equipment.png` - Linux/web icon
- `MANIFEST.in` - Ensures icons are included in source distributions

---

## Version History

- **v0.6.0** (2026-01-06): Updated all spec files to use "Test Equipment" icon set
- **v0.5.1** (2026-01-05): Initial icon configuration with "siglent-icon" files
