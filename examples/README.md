# Siglent Oscilloscope Control Examples

This directory contains example scripts demonstrating various features of the Siglent oscilloscope control package.

## Examples

### basic_usage.py
Basic oscilloscope control demonstrating:
- Connecting to the oscilloscope
- Configuring channels (coupling, scale, offset, probe ratio)
- Setting up triggers
- Performing measurements

**Usage:**
```bash
python basic_usage.py
```

### waveform_capture.py
Waveform acquisition and export demonstrating:
- Capturing waveform data from a channel
- Saving waveform to CSV file
- Plotting waveform with matplotlib
- Exporting plot to PNG image

**Usage:**
```bash
python waveform_capture.py
```

**Output:**
- `waveform.csv` - Waveform data in CSV format
- `waveform.png` - Waveform plot image

### measurements.py
Automated measurements demonstrating:
- Individual measurements (frequency, Vpp, RMS, period, etc.)
- Batch measurements on a channel
- Using the measurement API

**Usage:**
```bash
python measurements.py
```

### live_plot.py
Real-time waveform plotting demonstrating:
- Live waveform acquisition
- Animated matplotlib plotting
- Multi-channel display

**Usage:**
```bash
python live_plot.py
```

**Note:** Close the plot window to stop the live view.

## Configuration

Before running the examples, update the `SCOPE_IP` variable in each script to match your oscilloscope's IP address.

To find your oscilloscope's IP address:
1. Press **Utility** on the oscilloscope
2. Navigate to **I/O** settings
3. Check the **LAN** configuration

## Requirements

All examples require the siglent package to be installed:

```bash
cd /path/to/Siglent
pip install -e .
```

## Tips

- Make sure your oscilloscope is connected to the same network as your computer
- Ensure the SCPI port (5024) is accessible
- Some commands may vary slightly between oscilloscope models - refer to your programming manual
- Enable at least one channel before capturing waveforms
- Use AUTO trigger mode for continuous acquisition
- Use NORMAL or SINGLE mode for specific trigger conditions
