"""Waveform acquisition and data processing for Siglent oscilloscopes."""

from typing import TYPE_CHECKING, Optional, Tuple
from dataclasses import dataclass
import struct
import logging

import numpy as np

from siglent import exceptions

if TYPE_CHECKING:
    from siglent.oscilloscope import Oscilloscope

logger = logging.getLogger(__name__)


@dataclass
class WaveformData:
    """Container for waveform data and metadata.

    Attributes:
        time: Time values in seconds (numpy array)
        voltage: Voltage values in volts (numpy array)
        channel: Source channel number
        sample_rate: Sampling rate in samples/second
        record_length: Number of samples
        timebase: Timebase setting (seconds/division)
        voltage_scale: Voltage scale (volts/division)
        voltage_offset: Voltage offset in volts
    """

    time: np.ndarray
    voltage: np.ndarray
    channel: int
    sample_rate: float
    record_length: int
    timebase: float
    voltage_scale: float
    voltage_offset: float

    def __len__(self) -> int:
        """Get number of samples."""
        return len(self.voltage)


class Waveform:
    """Waveform acquisition and data processing.

    Handles downloading waveform data from oscilloscope channels and
    converting to voltage/time arrays.
    """

    def __init__(self, oscilloscope: "Oscilloscope"):
        """Initialize waveform acquisition.

        Args:
            oscilloscope: Parent Oscilloscope instance
        """
        self._scope = oscilloscope

    def acquire(self, channel: int, format: str = "BYTE") -> WaveformData:
        """Acquire waveform data from a channel.

        Args:
            channel: Channel number (1-4)
            format: Data format - 'BYTE' or 'WORD' (default: 'BYTE')

        Returns:
            WaveformData object with time and voltage arrays

        Raises:
            InvalidParameterError: If channel number is invalid
            CommandError: If acquisition fails
        """
        if not 1 <= channel <= 4:
            raise exceptions.InvalidParameterError(f"Invalid channel number: {channel}. Must be 1-4.")

        logger.info(f"Acquiring waveform from channel {channel}")

        # Get channel configuration
        ch = f"C{channel}"
        voltage_scale = self._get_voltage_scale(ch)
        voltage_offset = self._get_voltage_offset(ch)
        timebase = self._get_timebase()
        sample_rate = self._get_sample_rate()

        # Request waveform data
        waveform_command = f"{ch}:WF? DAT2"  # DAT2 is binary format
        self._scope.write(waveform_command)

        # Read waveform data header and data
        raw_data = self._scope.read_raw()

        # Parse waveform data
        voltage_data = self._parse_waveform(raw_data, format)
        record_length = len(voltage_data)

        # Convert to voltage using scale and offset
        # Formula: Voltage = (code - code_offset) * code_scale + voltage_offset
        # For 8-bit data: typically code_offset = 127 (or 128), code_scale = voltage_scale / 25
        voltage = self._convert_to_voltage(voltage_data, voltage_scale, voltage_offset)

        # Generate time axis
        time = self._generate_time_axis(record_length, sample_rate, timebase)

        logger.info(f"Acquired {record_length} samples from channel {channel}")

        return WaveformData(
            time=time,
            voltage=voltage,
            channel=channel,
            sample_rate=sample_rate,
            record_length=record_length,
            timebase=timebase,
            voltage_scale=voltage_scale,
            voltage_offset=voltage_offset,
        )

    def _get_voltage_scale(self, channel: str) -> float:
        """Get voltage scale for channel.

        Args:
            channel: Channel name (e.g., 'C1')

        Returns:
            Voltage scale in V/div
        """
        response = self._scope.query(f"{channel}:VDIV?")
        value = response.replace("V", "").strip()
        return float(value)

    def _get_voltage_offset(self, channel: str) -> float:
        """Get voltage offset for channel.

        Args:
            channel: Channel name (e.g., 'C1')

        Returns:
            Voltage offset in volts
        """
        response = self._scope.query(f"{channel}:OFST?")
        value = response.replace("V", "").strip()
        return float(value)

    def _get_timebase(self) -> float:
        """Get timebase setting.

        Returns:
            Timebase in seconds/division
        """
        response = self._scope.query("TDIV?")
        value = response.replace("S", "").strip()
        return float(value)

    def _get_sample_rate(self) -> float:
        """Get sample rate.

        Returns:
            Sample rate in samples/second
        """
        response = self._scope.query("SARA?")
        # Response format may vary: "1.00E+09Sa/s" or similar
        value = response.replace("Sa/s", "").replace("SA/S", "").strip()
        return float(value)

    def _parse_waveform(self, raw_data: bytes, format: str = "BYTE") -> np.ndarray:
        """Parse waveform data from oscilloscope.

        Args:
            raw_data: Raw binary data from oscilloscope
            format: Data format - 'BYTE' or 'WORD'

        Returns:
            Numpy array of raw data codes
        """
        # Siglent waveform format:
        # Header: DESC,#9000000346...
        # Find the start of binary data (after header)

        # Look for the # character indicating block data
        header_end = raw_data.find(b"#")
        if header_end == -1:
            raise exceptions.CommandError("Invalid waveform format: no # found")

        # Parse IEEE 488.2 definite length block
        # Format: #<n><length><data>
        # where n is number of digits in length
        n_digits = int(chr(raw_data[header_end + 1]))
        data_length = int(raw_data[header_end + 2 : header_end + 2 + n_digits])
        data_start = header_end + 2 + n_digits

        # Extract binary data
        binary_data = raw_data[data_start : data_start + data_length]

        # Convert to numpy array
        if format == "BYTE":
            # 8-bit signed data
            data = np.frombuffer(binary_data, dtype=np.int8)
        elif format == "WORD":
            # 16-bit signed data
            data = np.frombuffer(binary_data, dtype=np.int16)
        else:
            raise exceptions.InvalidParameterError(f"Invalid format: {format}")

        return data

    def _convert_to_voltage(self, codes: np.ndarray, voltage_scale: float, voltage_offset: float) -> np.ndarray:
        """Convert raw ADC codes to voltage values.

        Args:
            codes: Raw ADC code values
            voltage_scale: Voltage scale (V/div)
            voltage_offset: Voltage offset (V)

        Returns:
            Voltage array in volts
        """
        # Siglent conversion formula (for 8-bit data):
        # voltage = (code - 127) * voltage_scale / 25 - voltage_offset
        # The factor 25 is because there are ~25 codes per division in 8-bit mode

        # For 8-bit data
        if codes.dtype == np.int8:
            code_per_div = 25.0
            code_center = 0  # Since it's signed int8, center is 0
        else:  # 16-bit data
            code_per_div = 6400.0
            code_center = 0

        # Convert codes to voltage
        voltage = (codes.astype(np.float64) - code_center) * (voltage_scale / code_per_div) - voltage_offset

        return voltage

    def _generate_time_axis(self, num_samples: int, sample_rate: float, timebase: float) -> np.ndarray:
        """Generate time axis for waveform.

        Args:
            num_samples: Number of samples
            sample_rate: Sample rate in Sa/s
            timebase: Timebase in s/div

        Returns:
            Time array in seconds
        """
        # Calculate time interval
        dt = 1.0 / sample_rate

        # Generate time axis (centered at trigger point)
        # Typically trigger is at center of screen (14 divisions total, 7 left of trigger)
        total_time = num_samples * dt
        trigger_position = total_time / 2  # Assume trigger at center

        time = np.arange(num_samples) * dt - trigger_position

        return time

    def get_waveform_preamble(self, channel: int) -> dict:
        """Get waveform preamble information.

        Args:
            channel: Channel number (1-4)

        Returns:
            Dictionary with waveform metadata
        """
        if not 1 <= channel <= 4:
            raise exceptions.InvalidParameterError(f"Invalid channel number: {channel}. Must be 1-4.")

        ch = f"C{channel}"

        return {
            "channel": channel,
            "voltage_scale": self._get_voltage_scale(ch),
            "voltage_offset": self._get_voltage_offset(ch),
            "timebase": self._get_timebase(),
            "sample_rate": self._get_sample_rate(),
        }

    def save_waveform(self, waveform: WaveformData, filename: str, format: str = "CSV") -> None:
        """Save waveform data to file.

        Args:
            waveform: WaveformData object to save
            filename: Output filename
            format: File format - 'CSV' or 'NPY' (default: 'CSV')
        """
        if format.upper() == "CSV":
            # Save as CSV
            import csv

            with open(filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Time (s)", "Voltage (V)"])
                for t, v in zip(waveform.time, waveform.voltage):
                    writer.writerow([t, v])
            logger.info(f"Waveform saved to {filename} (CSV format)")

        elif format.upper() == "NPY":
            # Save as NumPy binary
            np.savez(
                filename,
                time=waveform.time,
                voltage=waveform.voltage,
                channel=waveform.channel,
                sample_rate=waveform.sample_rate,
            )
            logger.info(f"Waveform saved to {filename} (NPY format)")

        else:
            raise exceptions.InvalidParameterError(f"Invalid format: {format}")

    def __repr__(self) -> str:
        """String representation."""
        return "Waveform()"
