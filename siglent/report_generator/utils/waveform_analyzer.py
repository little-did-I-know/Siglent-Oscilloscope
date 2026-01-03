"""
Waveform analyzer for calculating signal statistics.

Automatically computes frequency, amplitude, timing, and quality metrics
from oscilloscope waveform data.
"""

import numpy as np
from typing import Dict, Optional, Tuple
from scipy import signal as scipy_signal
from scipy.fft import fft, fftfreq

from siglent.report_generator.models.report_data import WaveformData


class WaveformAnalyzer:
    """Analyzes waveform data to extract signal statistics."""

    @staticmethod
    def analyze(waveform: WaveformData) -> Dict[str, Optional[float]]:
        """
        Analyze a waveform and calculate all statistics.

        Args:
            waveform: Waveform data to analyze

        Returns:
            Dictionary of calculated statistics
        """
        stats = {}

        # Amplitude measurements
        stats.update(WaveformAnalyzer.calculate_amplitude_stats(waveform))

        # Frequency and period
        stats.update(WaveformAnalyzer.calculate_frequency_stats(waveform))

        # Timing measurements
        stats.update(WaveformAnalyzer.calculate_timing_stats(waveform))

        # Signal quality metrics
        stats.update(WaveformAnalyzer.calculate_quality_stats(waveform))

        return stats

    @staticmethod
    def calculate_amplitude_stats(waveform: WaveformData) -> Dict[str, float]:
        """Calculate amplitude-related statistics."""
        v = waveform.voltage_data

        vmax = np.max(v)
        vmin = np.min(v)
        vpp = vmax - vmin
        vmean = np.mean(v)
        vrms = np.sqrt(np.mean(v ** 2))
        vamp = (vmax + vmin) / 2  # Amplitude (middle of range)

        return {
            'vmax': vmax,
            'vmin': vmin,
            'vpp': vpp,
            'vmean': vmean,
            'vrms': vrms,
            'vamp': vamp,
            'dc_offset': vmean,
        }

    @staticmethod
    def calculate_frequency_stats(waveform: WaveformData) -> Dict[str, Optional[float]]:
        """Calculate frequency and period using FFT."""
        try:
            v = waveform.voltage_data
            sample_rate = waveform.sample_rate

            # Compute FFT
            n = len(v)
            yf = fft(v)
            xf = fftfreq(n, 1/sample_rate)

            # Get positive frequencies only
            pos_mask = xf > 0
            xf_pos = xf[pos_mask]
            yf_pos = np.abs(yf[pos_mask])

            # Find peak frequency (excluding DC component)
            if len(yf_pos) > 1:
                # Skip first bin (DC)
                peak_idx = np.argmax(yf_pos[1:]) + 1
                frequency = xf_pos[peak_idx]
                period = 1 / frequency if frequency > 0 else None

                return {
                    'frequency': frequency,
                    'period': period,
                }
            else:
                return {
                    'frequency': None,
                    'period': None,
                }

        except Exception as e:
            print(f"Error calculating frequency: {e}")
            return {
                'frequency': None,
                'period': None,
            }

    @staticmethod
    def calculate_timing_stats(waveform: WaveformData) -> Dict[str, Optional[float]]:
        """Calculate timing measurements (rise time, fall time, pulse width, duty cycle)."""
        try:
            v = waveform.voltage_data
            t = waveform.time_data
            dt = np.mean(np.diff(t))  # Average time step

            vmax = np.max(v)
            vmin = np.min(v)
            vrange = vmax - vmin

            # Thresholds for timing measurements
            v_low = vmin + 0.1 * vrange  # 10%
            v_high = vmin + 0.9 * vrange  # 90%
            v_50 = vmin + 0.5 * vrange   # 50%

            # Find edges (zero crossings of derivative)
            dv = np.diff(v)
            rising_edges = np.where((v[:-1] < v_50) & (v[1:] >= v_50))[0]
            falling_edges = np.where((v[:-1] > v_50) & (v[1:] <= v_50))[0]

            rise_time = None
            fall_time = None
            pulse_width = None
            duty_cycle = None

            # Calculate rise time (first rising edge)
            if len(rising_edges) > 0:
                edge_idx = rising_edges[0]
                # Find 10% and 90% points around this edge
                start_idx = edge_idx
                while start_idx > 0 and v[start_idx] > v_low:
                    start_idx -= 1
                end_idx = edge_idx
                while end_idx < len(v) - 1 and v[end_idx] < v_high:
                    end_idx += 1

                if end_idx > start_idx:
                    rise_time = (end_idx - start_idx) * dt

            # Calculate fall time (first falling edge)
            if len(falling_edges) > 0:
                edge_idx = falling_edges[0]
                start_idx = edge_idx
                while start_idx > 0 and v[start_idx] < v_high:
                    start_idx -= 1
                end_idx = edge_idx
                while end_idx < len(v) - 1 and v[end_idx] > v_low:
                    end_idx += 1

                if end_idx > start_idx:
                    fall_time = (end_idx - start_idx) * dt

            # Calculate pulse width and duty cycle
            if len(rising_edges) > 0 and len(falling_edges) > 0:
                # Pulse width: time from rising edge to next falling edge
                if falling_edges[0] > rising_edges[0]:
                    pulse_width = (falling_edges[0] - rising_edges[0]) * dt

                # Duty cycle: ratio of high time to period
                if len(rising_edges) > 1:
                    period_samples = rising_edges[1] - rising_edges[0]
                    high_samples = falling_edges[0] - rising_edges[0] if falling_edges[0] > rising_edges[0] else 0
                    duty_cycle = (high_samples / period_samples) * 100  # Percentage

            return {
                'rise_time': rise_time,
                'fall_time': fall_time,
                'pulse_width': pulse_width,
                'duty_cycle': duty_cycle,
            }

        except Exception as e:
            print(f"Error calculating timing stats: {e}")
            return {
                'rise_time': None,
                'fall_time': None,
                'pulse_width': None,
                'duty_cycle': None,
            }

    @staticmethod
    def calculate_quality_stats(waveform: WaveformData) -> Dict[str, Optional[float]]:
        """Calculate signal quality metrics (SNR, noise, overshoot, undershoot, jitter)."""
        try:
            v = waveform.voltage_data

            # Estimate noise level (high-frequency component)
            # Use standard deviation of detrended signal
            v_detrended = v - np.mean(v)
            noise_level = np.std(v_detrended)

            # Signal to Noise Ratio (SNR)
            vmax = np.max(v)
            vmin = np.min(v)
            signal_amplitude = (vmax - vmin) / 2
            snr = 20 * np.log10(signal_amplitude / noise_level) if noise_level > 0 else None

            # Overshoot and undershoot (percentage above/below steady-state levels)
            # This is approximate - we'll use top 10% and bottom 10% as steady state
            v_sorted = np.sort(v)
            n = len(v_sorted)
            v_high_steady = np.mean(v_sorted[int(0.85*n):int(0.95*n)])  # High steady state
            v_low_steady = np.mean(v_sorted[int(0.05*n):int(0.15*n)])   # Low steady state

            overshoot = ((vmax - v_high_steady) / (v_high_steady - v_low_steady)) * 100 if v_high_steady != v_low_steady else 0
            undershoot = ((v_low_steady - vmin) / (v_high_steady - v_low_steady)) * 100 if v_high_steady != v_low_steady else 0

            # Jitter (standard deviation of edge timing)
            # Find all rising edges
            v_50 = (vmax + vmin) / 2
            rising_edges = np.where((v[:-1] < v_50) & (v[1:] >= v_50))[0]

            jitter = None
            if len(rising_edges) > 2:
                # Calculate period jitter
                periods = np.diff(rising_edges)
                jitter = np.std(periods) * np.mean(np.diff(waveform.time_data))

            return {
                'noise_level': noise_level,
                'snr': snr,
                'overshoot': max(0, overshoot),  # Don't show negative overshoot
                'undershoot': max(0, undershoot),  # Don't show negative undershoot
                'jitter': jitter,
            }

        except Exception as e:
            print(f"Error calculating quality stats: {e}")
            return {
                'noise_level': None,
                'snr': None,
                'overshoot': None,
                'undershoot': None,
                'jitter': None,
            }

    @staticmethod
    def format_stat_value(name: str, value: Optional[float]) -> str:
        """
        Format a statistic value with appropriate units and precision.

        Args:
            name: Statistic name
            value: Value to format

        Returns:
            Formatted string with value and units
        """
        if value is None:
            return "N/A"

        # Voltage measurements
        if name in ['vmax', 'vmin', 'vpp', 'vmean', 'vrms', 'vamp', 'dc_offset', 'noise_level']:
            if abs(value) >= 1:
                return f"{value:.3f} V"
            elif abs(value) >= 0.001:
                return f"{value*1000:.2f} mV"
            else:
                return f"{value*1e6:.2f} µV"

        # Frequency
        elif name == 'frequency':
            if value >= 1e6:
                return f"{value/1e6:.3f} MHz"
            elif value >= 1e3:
                return f"{value/1e3:.3f} kHz"
            else:
                return f"{value:.2f} Hz"

        # Time measurements
        elif name in ['period', 'rise_time', 'fall_time', 'pulse_width', 'jitter']:
            if value >= 1:
                return f"{value:.3f} s"
            elif value >= 1e-3:
                return f"{value*1e3:.3f} ms"
            elif value >= 1e-6:
                return f"{value*1e6:.3f} µs"
            else:
                return f"{value*1e9:.2f} ns"

        # Percentage
        elif name in ['duty_cycle', 'overshoot', 'undershoot']:
            return f"{value:.2f} %"

        # SNR (dB)
        elif name == 'snr':
            return f"{value:.2f} dB"

        # Default
        else:
            return f"{value:.4g}"
