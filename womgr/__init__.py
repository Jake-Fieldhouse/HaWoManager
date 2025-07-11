"""Simple device management utilities."""

from .entities import (
    ConfigEntry,
    PingBinarySensor,
    SystemCommandSwitch,
    WakeOnLanSwitch,
    setup_device,
    remove_device,
)
from .util import pastel_color, slugify

__all__ = [
    "ConfigEntry",
    "PingBinarySensor",
    "SystemCommandSwitch",
    "WakeOnLanSwitch",
    "setup_device",
    "remove_device",
    "pastel_color",
    "slugify",
]
