"""Main Oscilloscope class for controlling Siglent SD824x HD oscilloscopes."""

from typing import Optional, Dict, Any
import logging

from siglent.connection import SocketConnection, BaseConnection
from siglent import exceptions

from siglent.channel import Channel
from siglent.trigger import Trigger
from siglent.waveform import Waveform, WaveformData
from siglent.measurement import Measurement

logger = logging.getLogger(__name__)


class Oscilloscope:
    """Main class for controlling Siglent SD824x HD oscilloscopes.

    This class provides a high-level interface for controlling oscilloscope
    functions including channels, triggers, waveform acquisition, and measurements.

    Example:
        >>> scope = Oscilloscope('192.168.1.100')
        >>> scope.connect()
        >>> print(scope.identify())
        >>> scope.disconnect()

        Or using context manager:
        >>> with Oscilloscope('192.168.1.100') as scope:
        ...     print(scope.identify())
    """

    def __init__(self, host: str, port: int = 5024, timeout: float = 5.0, connection: Optional[BaseConnection] = None):
        """Initialize oscilloscope connection.

        Args:
            host: IP address or hostname of the oscilloscope
            port: TCP port for SCPI communication (default: 5024)
            timeout: Command timeout in seconds (default: 5.0)
            connection: Optional custom connection object (uses SocketConnection if None)
        """
        self.host = host
        self.port = port
        self.timeout = timeout

        # Create connection
        if connection is not None:
            self._connection = connection
        else:
            self._connection = SocketConnection(host, port, timeout)

        # Device information (populated after connection)
        self._device_info: Optional[Dict[str, str]] = None

        # Initialize channels (1-4 for SD824x)
        self.channel1 = Channel(self, 1)
        self.channel2 = Channel(self, 2)
        self.channel3 = Channel(self, 3)
        self.channel4 = Channel(self, 4)

        # Initialize trigger control
        self.trigger = Trigger(self)

        # Initialize waveform acquisition
        self.waveform = Waveform(self)

        # Initialize measurement control
        self.measurement = Measurement(self)

    def connect(self) -> None:
        """Establish connection to the oscilloscope.

        Raises:
            ConnectionError: If connection fails
        """
        logger.info(f"Connecting to oscilloscope at {self.host}:{self.port}")
        self._connection.connect()
        logger.info("Connected successfully")

        # Verify connection by getting device identification
        try:
            self._device_info = self._parse_idn(self.identify())
            logger.info(f"Connected to: {self._device_info.get('model', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to identify device: {e}")
            self.disconnect()
            raise exceptions.ConnectionError(f"Connected but failed to identify device: {e}")

    def disconnect(self) -> None:
        """Close connection to the oscilloscope."""
        logger.info("Disconnecting from oscilloscope")
        self._connection.disconnect()
        self._device_info = None

    @property
    def is_connected(self) -> bool:
        """Check if connected to oscilloscope.

        Returns:
            True if connected, False otherwise
        """
        return self._connection.is_connected

    def write(self, command: str) -> None:
        """Send a SCPI command to the oscilloscope.

        Args:
            command: SCPI command string

        Raises:
            ConnectionError: If not connected
        """
        logger.debug(f"Write: {command}")
        self._connection.write(command)

    def query(self, command: str) -> str:
        """Send a SCPI query and get the response.

        Args:
            command: SCPI query command

        Returns:
            Response string from oscilloscope

        Raises:
            ConnectionError: If not connected
        """
        logger.debug(f"Query: {command}")
        response = self._connection.query(command)
        logger.debug(f"Response: {response}")
        return response

    def read_raw(self, size: Optional[int] = None) -> bytes:
        """Read raw binary data from oscilloscope.

        Args:
            size: Number of bytes to read (None for all available)

        Returns:
            Raw binary data
        """
        return self._connection.read_raw(size)

    def identify(self) -> str:
        """Get device identification string.

        Returns:
            Device identification string (manufacturer, model, serial, firmware)

        Example:
            'Siglent Technologies,SDS824X HD,SERIAL123,1.0.0.0'
        """
        return self.query("*IDN?")

    def reset(self) -> None:
        """Reset oscilloscope to default settings.

        Note: This may take several seconds to complete.
        """
        logger.info("Resetting oscilloscope to defaults")
        self.write("*RST")

    def clear_status(self) -> None:
        """Clear status registers."""
        self.write("*CLS")

    def get_error(self) -> str:
        """Get the last error from the error queue.

        Returns:
            Error string (format: "code,description")
        """
        return self.query("SYST:ERR?")

    def wait_complete(self) -> None:
        """Wait for all pending operations to complete."""
        self.query("*OPC?")

    def trigger_single(self) -> None:
        """Set trigger mode to single and force a trigger."""
        self.write("TRIG_MODE SINGLE")
        self.write("ARM")

    def trigger_force(self) -> None:
        """Force a trigger event."""
        self.write("FRTR")

    def run(self) -> None:
        """Start acquisition (set to AUTO trigger mode)."""
        self.write("TRIG_MODE AUTO")

    def stop(self) -> None:
        """Stop acquisition."""
        self.write("STOP")

    def auto_setup(self) -> None:
        """Perform automatic setup."""
        self.write("ASET")

    def get_waveform(self, channel: int) -> WaveformData:
        """Acquire waveform data from a channel.

        Convenience method that calls waveform.acquire().

        Args:
            channel: Channel number (1-4)

        Returns:
            WaveformData object with time and voltage arrays
        """
        return self.waveform.acquire(channel)

    @property
    def device_info(self) -> Optional[Dict[str, str]]:
        """Get parsed device information.

        Returns:
            Dictionary with keys: manufacturer, model, serial, firmware
            None if not connected
        """
        return self._device_info

    def _parse_idn(self, idn: str) -> Dict[str, str]:
        """Parse *IDN? response into dictionary.

        Args:
            idn: Identification string from *IDN? query

        Returns:
            Dictionary with manufacturer, model, serial, firmware
        """
        parts = idn.split(",")
        return {
            "manufacturer": parts[0].strip() if len(parts) > 0 else "",
            "model": parts[1].strip() if len(parts) > 1 else "",
            "serial": parts[2].strip() if len(parts) > 2 else "",
            "firmware": parts[3].strip() if len(parts) > 3 else "",
        }

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False

    def __repr__(self) -> str:
        """String representation."""
        if self.is_connected and self._device_info:
            model = self._device_info.get("model", "Unknown")
            return f"Oscilloscope({model} at {self.host}:{self.port})"
        return f"Oscilloscope({self.host}:{self.port}, disconnected)"
