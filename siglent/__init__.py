"""Siglent Oscilloscope Control Package

This package provides programmatic control for Siglent SD824x HD oscilloscopes
via Ethernet/LAN connection.

For high-level automation and data collection, see the automation module:
    from siglent.automation import DataCollector, TriggerWaitCollector
"""

__version__ = "0.1.0"

from siglent.exceptions import CommandError, ConnectionError, SiglentError, TimeoutError
from siglent.oscilloscope import Oscilloscope

__all__ = [
    "Oscilloscope",
    "SiglentError",
    "ConnectionError",
    "TimeoutError",
    "CommandError",
]
