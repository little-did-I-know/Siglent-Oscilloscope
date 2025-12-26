"""Waveform display widget using matplotlib."""

import logging
from typing import Optional, Dict, List

import numpy as np
import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox, QLabel, QGroupBox, QFileDialog
from PyQt6.QtCore import Qt

from siglent.waveform import WaveformData

logger = logging.getLogger(__name__)


class WaveformDisplay(QWidget):
    """Widget for displaying oscilloscope waveforms using matplotlib.

    Features:
    - Multiple channel display with different colors
    - Grid toggle
    - Autoscale
    - Zoom and pan (via matplotlib toolbar)
    - Export to image
    """

    # Channel colors (matching typical oscilloscope colors)
    CHANNEL_COLORS = {
        1: "#FFD700",  # Yellow/Gold
        2: "#00CED1",  # Cyan
        3: "#FF1493",  # Deep Pink/Magenta
        4: "#00FF00",  # Green
    }

    def __init__(self, parent=None):
        """Initialize waveform display widget.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        self.waveforms: Dict[int, WaveformData] = {}  # Store waveforms by channel
        self.show_grid = True

        self._init_ui()
        logger.info("Waveform display widget initialized")

    def _init_ui(self):
        """Initialize user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(10, 6), facecolor="#1a1a1a")
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111, facecolor="#0a0a0a")

        # Configure axes
        self._configure_axes()

        # Create navigation toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)

        # Create control panel
        control_panel = self._create_control_panel()

        # Add to layout
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=1)
        layout.addWidget(control_panel)

    def _configure_axes(self):
        """Configure matplotlib axes appearance."""
        # Set dark theme colors
        self.ax.set_facecolor("#0a0a0a")
        self.ax.tick_params(colors="#888888", which="both")
        self.ax.spines["bottom"].set_color("#444444")
        self.ax.spines["top"].set_color("#444444")
        self.ax.spines["left"].set_color("#444444")
        self.ax.spines["right"].set_color("#444444")

        # Set labels
        self.ax.set_xlabel("Time (s)", color="#cccccc", fontsize=10)
        self.ax.set_ylabel("Voltage (V)", color="#cccccc", fontsize=10)
        self.ax.set_title("Waveform Display", color="#cccccc", fontsize=12)

        # Enable grid
        self.ax.grid(True, alpha=0.3, color="#444444", linestyle="--", linewidth=0.5)

        # Tight layout
        self.figure.tight_layout()

    def _create_control_panel(self) -> QWidget:
        """Create control panel with buttons.

        Returns:
            Control panel widget
        """
        panel = QWidget()
        layout = QHBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)

        # Grid toggle
        self.grid_checkbox = QCheckBox("Grid")
        self.grid_checkbox.setChecked(self.show_grid)
        self.grid_checkbox.stateChanged.connect(self._on_grid_toggle)
        layout.addWidget(self.grid_checkbox)

        # Autoscale button
        autoscale_btn = QPushButton("Autoscale")
        autoscale_btn.clicked.connect(self._on_autoscale)
        layout.addWidget(autoscale_btn)

        # Clear button
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._on_clear)
        layout.addWidget(clear_btn)

        # Export button
        export_btn = QPushButton("Export Image...")
        export_btn.clicked.connect(self._on_export)
        layout.addWidget(export_btn)

        # Channel info label
        self.info_label = QLabel("No data")
        self.info_label.setStyleSheet("color: #888888;")
        layout.addWidget(self.info_label, stretch=1)

        return panel

    def plot_waveform(self, waveform: WaveformData, clear_others: bool = False):
        """Plot a waveform on the display.

        Args:
            waveform: WaveformData object to plot
            clear_others: If True, clear other channels before plotting
        """
        if clear_others:
            self.waveforms.clear()

        # Store waveform
        self.waveforms[waveform.channel] = waveform

        # Replot all waveforms
        self._replot()

        logger.info(f"Plotted waveform from channel {waveform.channel}")

    def plot_multiple_waveforms(self, waveforms: List[WaveformData]):
        """Plot multiple waveforms.

        Args:
            waveforms: List of WaveformData objects to plot
        """
        self.waveforms.clear()

        for waveform in waveforms:
            self.waveforms[waveform.channel] = waveform

        self._replot()

        logger.info(f"Plotted {len(waveforms)} waveforms")

    def update_waveform(self, waveform: WaveformData):
        """Update existing waveform or add new one.

        Args:
            waveform: WaveformData object to update/add
        """
        self.waveforms[waveform.channel] = waveform
        self._replot()

    def clear_channel(self, channel: int):
        """Clear waveform for a specific channel.

        Args:
            channel: Channel number to clear (1-4)
        """
        if channel in self.waveforms:
            del self.waveforms[channel]
            self._replot()
            logger.info(f"Cleared channel {channel}")

    def clear_all(self):
        """Clear all waveforms."""
        self.waveforms.clear()
        self._replot()
        logger.info("Cleared all waveforms")

    def _replot(self):
        """Replot all stored waveforms."""
        # Clear axes
        self.ax.clear()

        # Reconfigure axes
        self._configure_axes()

        if not self.waveforms:
            # No data to plot
            self.ax.text(0.5, 0.5, "No waveform data", horizontalalignment="center", verticalalignment="center", transform=self.ax.transAxes, color="#888888", fontsize=14)
            self.info_label.setText("No data")
        else:
            # Plot each channel
            for channel, waveform in sorted(self.waveforms.items()):
                color = self.CHANNEL_COLORS.get(channel, "#FFFFFF")
                label = f"CH{channel}"

                # Convert time to appropriate units
                time_data, time_unit = self._convert_time_units(waveform.time)

                # Plot waveform
                self.ax.plot(time_data, waveform.voltage, color=color, linewidth=1.0, label=label, alpha=0.9)

            # Update x-axis label with appropriate time unit
            self.ax.set_xlabel(f"Time ({time_unit})", color="#cccccc", fontsize=10)

            # Add legend
            legend = self.ax.legend(loc="upper right", framealpha=0.8, facecolor="#1a1a1a", edgecolor="#444444")
            for text in legend.get_texts():
                text.set_color("#cccccc")

            # Update info label
            num_channels = len(self.waveforms)
            total_samples = sum(len(w) for w in self.waveforms.values())
            self.info_label.setText(f"{num_channels} channel(s) | {total_samples} total samples")

        # Apply grid setting
        self.ax.grid(self.show_grid, alpha=0.3, color="#444444", linestyle="--", linewidth=0.5)

        # Redraw canvas
        self.canvas.draw()

    def _convert_time_units(self, time: np.ndarray) -> tuple:
        """Convert time array to appropriate units.

        Args:
            time: Time array in seconds

        Returns:
            Tuple of (converted_time, unit_string)
        """
        # Determine appropriate time unit
        max_time = np.max(np.abs(time))

        if max_time < 1e-6:  # Less than 1 microsecond
            return time * 1e9, "ns"
        elif max_time < 1e-3:  # Less than 1 millisecond
            return time * 1e6, "µs"
        elif max_time < 1:  # Less than 1 second
            return time * 1e3, "ms"
        else:
            return time, "s"

    def _on_grid_toggle(self, state):
        """Handle grid toggle.

        Args:
            state: Checkbox state
        """
        self.show_grid = bool(state)
        self.ax.grid(self.show_grid, alpha=0.3, color="#444444", linestyle="--", linewidth=0.5)
        self.canvas.draw()
        logger.debug(f"Grid {'enabled' if self.show_grid else 'disabled'}")

    def _on_autoscale(self):
        """Handle autoscale button click."""
        self.ax.autoscale(enable=True, axis="both", tight=False)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        logger.debug("Autoscale applied")

    def _on_clear(self):
        """Handle clear button click."""
        self.clear_all()

    def _on_export(self):
        """Handle export button click."""
        if not self.waveforms:
            logger.warning("No waveform to export")
            return

        # Get filename from user
        filename, _ = QFileDialog.getSaveFileName(self, "Export Waveform Image", "waveform.png", "PNG Image (*.png);;PDF Document (*.pdf);;SVG Image (*.svg)")

        if filename:
            try:
                self.figure.savefig(filename, dpi=150, facecolor=self.figure.get_facecolor())
                logger.info(f"Exported waveform to {filename}")
            except Exception as e:
                logger.error(f"Failed to export waveform: {e}")

    def set_theme(self, dark: bool = True):
        """Set display theme.

        Args:
            dark: True for dark theme, False for light theme
        """
        if dark:
            # Dark theme (default)
            self.figure.set_facecolor("#1a1a1a")
            self.ax.set_facecolor("#0a0a0a")
            text_color = "#cccccc"
            grid_color = "#444444"
            spine_color = "#444444"
        else:
            # Light theme
            self.figure.set_facecolor("#ffffff")
            self.ax.set_facecolor("#f8f8f8")
            text_color = "#000000"
            grid_color = "#cccccc"
            spine_color = "#000000"

        # Update colors
        self.ax.tick_params(colors=text_color, which="both")
        self.ax.spines["bottom"].set_color(spine_color)
        self.ax.spines["top"].set_color(spine_color)
        self.ax.spines["left"].set_color(spine_color)
        self.ax.spines["right"].set_color(spine_color)
        self.ax.set_xlabel("Time", color=text_color)
        self.ax.set_ylabel("Voltage (V)", color=text_color)
        self.ax.set_title("Waveform Display", color=text_color)
        self.ax.grid(self.show_grid, alpha=0.3, color=grid_color)

        self.canvas.draw()
        logger.info(f"Theme set to {'dark' if dark else 'light'}")
