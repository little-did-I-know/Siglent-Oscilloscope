"""Main window for Siglent oscilloscope control GUI."""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QStatusBar, QMessageBox, QInputDialog,
    QGroupBox, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from siglent import Oscilloscope
from siglent.exceptions import ConnectionError, SiglentError
from siglent.gui.widgets.waveform_display import WaveformDisplay

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window for oscilloscope control."""

    def __init__(self):
        """Initialize main window."""
        super().__init__()

        self.scope: Optional[Oscilloscope] = None
        self.is_live_view = False
        self.live_timer = QTimer()
        self.live_timer.timeout.connect(self._update_live_view)

        self._init_ui()
        self._create_menus()
        self._create_toolbar()
        self._create_status_bar()

        logger.info("Main window initialized")

    def _init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("Siglent Oscilloscope Control")
        self.setGeometry(100, 100, 1400, 800)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Controls
        left_panel = self._create_control_panel()
        splitter.addWidget(left_panel)

        # Right panel - Waveform display
        right_panel = self._create_display_panel()
        splitter.addWidget(right_panel)

        # Set initial sizes (30% controls, 70% display)
        splitter.setSizes([400, 1000])

        main_layout.addWidget(splitter)

    def _create_control_panel(self) -> QWidget:
        """Create the left control panel.

        Returns:
            Control panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Connection group
        connection_group = QGroupBox("Connection")
        connection_layout = QVBoxLayout(connection_group)
        connection_layout.addWidget(QWidget())  # Placeholder for connection controls
        layout.addWidget(connection_group)

        # Create tab widget for controls
        tabs = QTabWidget()

        # Channels tab
        channels_widget = QWidget()
        channels_layout = QVBoxLayout(channels_widget)
        channels_layout.addWidget(QWidget())  # Placeholder - will add channel widgets
        tabs.addTab(channels_widget, "Channels")

        # Trigger tab
        trigger_widget = QWidget()
        trigger_layout = QVBoxLayout(trigger_widget)
        trigger_layout.addWidget(QWidget())  # Placeholder - will add trigger widget
        tabs.addTab(trigger_widget, "Trigger")

        # Measurements tab
        measurements_widget = QWidget()
        measurements_layout = QVBoxLayout(measurements_widget)
        measurements_layout.addWidget(QWidget())  # Placeholder - will add measurement widget
        tabs.addTab(measurements_widget, "Measurements")

        layout.addWidget(tabs)

        # Add stretch to push everything to top
        layout.addStretch()

        return panel

    def _create_display_panel(self) -> QWidget:
        """Create the right display panel.

        Returns:
            Display panel widget
        """
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Waveform display group
        display_group = QGroupBox("Waveform Display")
        display_layout = QVBoxLayout(display_group)
        display_layout.setContentsMargins(0, 0, 0, 0)

        # Create waveform display widget
        self.waveform_display = WaveformDisplay()
        display_layout.addWidget(self.waveform_display)

        layout.addWidget(display_group)

        return panel

    def _create_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        connect_action = QAction("&Connect...", self)
        connect_action.setShortcut("Ctrl+O")
        connect_action.triggered.connect(self._on_connect)
        file_menu.addAction(connect_action)

        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.triggered.connect(self._on_disconnect)
        file_menu.addAction(disconnect_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Acquisition menu
        acq_menu = menubar.addMenu("&Acquisition")

        run_action = QAction("&Run", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self._on_run)
        acq_menu.addAction(run_action)

        stop_action = QAction("&Stop", self)
        stop_action.setShortcut("F6")
        stop_action.triggered.connect(self._on_stop)
        acq_menu.addAction(stop_action)

        single_action = QAction("S&ingle", self)
        single_action.setShortcut("F7")
        single_action.triggered.connect(self._on_single)
        acq_menu.addAction(single_action)

        acq_menu.addSeparator()

        capture_action = QAction("&Capture Waveform", self)
        capture_action.setShortcut("F8")
        capture_action.triggered.connect(self._on_capture_waveform)
        acq_menu.addAction(capture_action)

        live_view_action = QAction("&Live View", self)
        live_view_action.setCheckable(True)
        live_view_action.toggled.connect(self._on_toggle_live_view)
        acq_menu.addAction(live_view_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        auto_setup_action = QAction("&Auto Setup", self)
        auto_setup_action.triggered.connect(self._on_auto_setup)
        view_menu.addAction(auto_setup_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _create_toolbar(self):
        """Create toolbar."""
        toolbar = self.addToolBar("Main Toolbar")

        # Add actions to toolbar
        connect_action = QAction("Connect", self)
        connect_action.triggered.connect(self._on_connect)
        toolbar.addAction(connect_action)

        disconnect_action = QAction("Disconnect", self)
        disconnect_action.triggered.connect(self._on_disconnect)
        toolbar.addAction(disconnect_action)

        toolbar.addSeparator()

        run_action = QAction("Run", self)
        run_action.triggered.connect(self._on_run)
        toolbar.addAction(run_action)

        stop_action = QAction("Stop", self)
        stop_action.triggered.connect(self._on_stop)
        toolbar.addAction(stop_action)

        single_action = QAction("Single", self)
        single_action.triggered.connect(self._on_single)
        toolbar.addAction(single_action)

        toolbar.addSeparator()

        capture_action = QAction("Capture Waveform", self)
        capture_action.triggered.connect(self._on_capture_waveform)
        toolbar.addAction(capture_action)

    def _create_status_bar(self):
        """Create status bar."""
        self.statusBar().showMessage("Not connected")

    def _on_connect(self):
        """Handle connect action."""
        # Get IP address from user
        ip, ok = QInputDialog.getText(
            self, "Connect to Oscilloscope",
            "Enter oscilloscope IP address:",
            text="192.168.1.100"
        )

        if ok and ip:
            try:
                self.statusBar().showMessage(f"Connecting to {ip}...")
                self.scope = Oscilloscope(ip)
                self.scope.connect()

                device_info = self.scope.device_info
                model = device_info.get('model', 'Unknown') if device_info else 'Unknown'

                self.statusBar().showMessage(f"Connected to {model} at {ip}")
                QMessageBox.information(
                    self, "Connected",
                    f"Successfully connected to {model}\nIP: {ip}"
                )
                logger.info(f"Connected to oscilloscope at {ip}")

            except (ConnectionError, SiglentError) as e:
                self.statusBar().showMessage("Connection failed")
                QMessageBox.critical(
                    self, "Connection Error",
                    f"Failed to connect to oscilloscope:\n{str(e)}"
                )
                logger.error(f"Connection failed: {e}")
                self.scope = None

    def _on_disconnect(self):
        """Handle disconnect action."""
        if self.scope:
            # Stop live view if running
            if self.is_live_view:
                self._on_toggle_live_view(False)

            self.scope.disconnect()
            self.scope = None
            self.statusBar().showMessage("Disconnected")
            logger.info("Disconnected from oscilloscope")
        else:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")

    def _on_run(self):
        """Handle run action."""
        if self.scope:
            try:
                self.scope.run()
                self.statusBar().showMessage("Acquisition running (AUTO trigger)")
                logger.info("Acquisition started")
            except SiglentError as e:
                QMessageBox.critical(self, "Error", f"Failed to start acquisition:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")

    def _on_stop(self):
        """Handle stop action."""
        if self.scope:
            try:
                self.scope.stop()
                self.statusBar().showMessage("Acquisition stopped")
                logger.info("Acquisition stopped")
            except SiglentError as e:
                QMessageBox.critical(self, "Error", f"Failed to stop acquisition:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")

    def _on_single(self):
        """Handle single trigger action."""
        if self.scope:
            try:
                self.scope.trigger_single()
                self.statusBar().showMessage("Single trigger armed")
                logger.info("Single trigger armed")
            except SiglentError as e:
                QMessageBox.critical(self, "Error", f"Failed to arm single trigger:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")

    def _on_auto_setup(self):
        """Handle auto setup action."""
        if self.scope:
            try:
                self.statusBar().showMessage("Running auto setup...")
                self.scope.auto_setup()
                self.statusBar().showMessage("Auto setup complete")
                logger.info("Auto setup complete")
            except SiglentError as e:
                QMessageBox.critical(self, "Error", f"Auto setup failed:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")

    def _on_capture_waveform(self):
        """Handle capture waveform action."""
        if not self.scope:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")
            return

        try:
            self.statusBar().showMessage("Capturing waveforms...")

            # Capture waveforms from all enabled channels
            waveforms = []
            for ch_num in range(1, 5):  # Channels 1-4
                try:
                    channel = getattr(self.scope, f"channel{ch_num}")
                    if channel.enabled:
                        waveform = self.scope.get_waveform(ch_num)
                        waveforms.append(waveform)
                        logger.info(f"Captured waveform from channel {ch_num}")
                except Exception as e:
                    logger.warning(f"Could not capture from channel {ch_num}: {e}")

            if waveforms:
                # Display waveforms
                self.waveform_display.plot_multiple_waveforms(waveforms)
                self.statusBar().showMessage(f"Captured {len(waveforms)} waveform(s)")
            else:
                self.statusBar().showMessage("No enabled channels")
                QMessageBox.information(
                    self, "No Data",
                    "No channels are enabled. Please enable at least one channel."
                )

        except SiglentError as e:
            self.statusBar().showMessage("Capture failed")
            QMessageBox.critical(self, "Capture Error", f"Failed to capture waveforms:\n{str(e)}")
            logger.error(f"Waveform capture failed: {e}")

    def _on_toggle_live_view(self, checked: bool):
        """Handle live view toggle.

        Args:
            checked: True to enable live view, False to disable
        """
        if not self.scope:
            QMessageBox.warning(self, "Not Connected", "No oscilloscope connected")
            return

        self.is_live_view = checked

        if checked:
            # Start live view
            self.live_timer.start(200)  # Update every 200ms
            self.statusBar().showMessage("Live view enabled")
            logger.info("Live view enabled")
        else:
            # Stop live view
            self.live_timer.stop()
            self.statusBar().showMessage("Live view disabled")
            logger.info("Live view disabled")

    def _update_live_view(self):
        """Update waveform display for live view."""
        if not self.scope or not self.scope.is_connected:
            self.live_timer.stop()
            self.is_live_view = False
            return

        try:
            # Acquire waveforms from enabled channels
            waveforms = []

            for ch_num in range(1, 5):  # Channels 1-4
                try:
                    channel = getattr(self.scope, f"channel{ch_num}")
                    if channel.enabled:
                        waveform = self.scope.get_waveform(ch_num)
                        waveforms.append(waveform)
                except Exception as e:
                    logger.debug(f"Could not acquire waveform from channel {ch_num}: {e}")

            # Update display
            if waveforms:
                self.waveform_display.plot_multiple_waveforms(waveforms)
            else:
                logger.debug("No enabled channels for live view")

        except Exception as e:
            logger.error(f"Error updating live view: {e}")
            # Don't stop live view on error, just skip this update

    def _on_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About",
            "<h3>Siglent Oscilloscope Control</h3>"
            "<p>Version 0.1.0</p>"
            "<p>Control application for Siglent SD824x HD oscilloscopes</p>"
            "<p>Python package for programmatic and GUI-based oscilloscope control</p>"
        )

    def closeEvent(self, event):
        """Handle window close event."""
        # Stop live view if running
        if self.is_live_view:
            self.live_timer.stop()

        # Disconnect from scope
        if self.scope:
            self.scope.disconnect()

        event.accept()
