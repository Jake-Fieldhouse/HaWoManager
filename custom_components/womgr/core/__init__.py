"""Simple device management utilities."""

from .entities import (
    ConfigEntry,
    PingBinarySensor,
    SystemCommandSwitch,
    WakeOnLanSwitch,
    setup_device,
    remove_device,
)

__all__ = [
    "ConfigEntry",
    "PingBinarySensor",
    "SystemCommandSwitch",
    "WakeOnLanSwitch",
    "setup_device",
    "remove_device",
]
