# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-12-25

### Added
- Initial release of Siglent oscilloscope control package
- Complete programmatic API for controlling Siglent SD824x HD oscilloscopes
- TCP/IP socket connection via SCPI protocol (port 5024)
- Full channel control (all 4 channels)
  - Voltage scale and offset configuration
  - Coupling mode (DC/AC/GND)
  - Probe ratio settings
  - Bandwidth limiting
- Comprehensive trigger control
  - Trigger modes (Auto, Normal, Single, Stop)
  - Edge trigger configuration
  - Source selection and level control
  - Slope and coupling settings
- Waveform acquisition and processing
  - Binary waveform download
  - Automatic voltage conversion
  - NumPy array output
  - CSV and NPY export formats
- Automated measurements
  - Frequency, period, Vpp, RMS, amplitude
  - Rise/fall time, duty cycle
  - Min/max/mean calculations
  - Cursor support
- PyQt6-based GUI application
  - Connection management dialog
  - Acquisition controls (Run/Stop/Single)
  - Live waveform view with configurable update rate
  - Single waveform capture
  - Multi-channel matplotlib display with oscilloscope-style theming
  - Interactive zoom and pan
  - Waveform export to PNG/PDF/SVG
- Console script entry point (`siglent-gui`)
- Comprehensive example scripts
  - Basic usage and configuration
  - Waveform capture and export
  - Automated measurements
  - Live plotting
- Full documentation
  - API documentation in README
  - PyPI deployment guide
  - Build instructions
  - Example scripts with explanations

### Technical Details
- Python 3.8+ support
- Dependencies: PyQt6, NumPy, Matplotlib
- MIT License
- Type hints throughout codebase
- Context manager support for oscilloscope connections
- Comprehensive error handling with custom exceptions

[0.1.0]: https://github.com/siglent-control/siglent/releases/tag/v0.1.0
