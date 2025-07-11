"""Simple device management utilities."""

from womgr.entities import (
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
