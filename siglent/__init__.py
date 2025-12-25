"""Siglent Oscilloscope Control Package

This package provides programmatic control for Siglent SD824x HD oscilloscopes
via Ethernet/LAN connection.
"""

__version__ = "0.1.0"

from siglent.oscilloscope import Oscilloscope
from siglent.exceptions import (
    SiglentError,
    ConnectionError,
    TimeoutError,
    CommandError,
)

__all__ = [
    "Oscilloscope",
    "SiglentError",
    "ConnectionError",
    "TimeoutError",
    "CommandError",
]
