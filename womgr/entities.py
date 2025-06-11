from dataclasses import dataclass, field
import ipaddress
import socket
import subprocess
import sys
import shutil
from typing import List

from .util import parse_mac_address


def _create_entity_id(device_name: str, entity: str) -> str:
    return f"womgr_{device_name}_{entity}"


_existing_devices: set[str] = set()


@dataclass
class ConfigEntry:
    """Simple representation of a device config entry."""

    device_name: str
    mac: str
    ip: str
    os_type: str
    location: str = ""
    username: str = ""
    password: str = ""
    entities: List["WoMgrEntity"] = field(default_factory=list)

    def add_entity(self, entity: "WoMgrEntity") -> None:
        self.entities.append(entity)
        entity.config_entry = self

    def remove_entities(self) -> None:
        self.entities.clear()


class WoMgrEntity:
    """Base entity with a consistent entity_id scheme."""

    def __init__(self, device_name: str, entity_type: str) -> None:
        self.device_name = device_name
        self.entity_id = _create_entity_id(device_name, entity_type)
        self.config_entry: ConfigEntry | None = None


class WakeOnLanSwitch(WoMgrEntity):
    """Switch that sends a Wake-on-LAN magic packet."""

    def __init__(self, device_name: str, mac: str) -> None:
        super().__init__(device_name, "wol")
        self.mac = mac

    def turn_on(self) -> None:
        mac_bytes = parse_mac_address(self.mac)
        packet = b"\xff" * 6 + mac_bytes * 16
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.sendto(packet, ("<broadcast>", 9))


class PingBinarySensor(WoMgrEntity):
    """Binary sensor that checks reachability via ping."""

    def __init__(self, device_name: str, ip: str) -> None:
        super().__init__(device_name, "ping")
        self.ip = ip
        self.is_on = False

    def update(self) -> bool:
        args = ["ping"]
        if sys.platform.startswith("win"):
            args += ["-n", "1", "-w", "1000", self.ip]
        else:
            args += ["-c", "1", "-W", "1", self.ip]
        result = subprocess.run(args, stdout=subprocess.DEVNULL)
        self.is_on = result.returncode == 0
        return self.is_on


class SystemCommandSwitch(WoMgrEntity):
    """Switch that issues restart or shutdown commands."""

    def __init__(self, device_name: str, os_type: str, username: str = "", password: str = "") -> None:
        super().__init__(device_name, "system")
        self.os_type = os_type.lower()
        self.username = username
        self.password = password
        self.process: subprocess.Popen | None = None

    def restart(self) -> None:
        if self.os_type == "windows":
            shutdown_bin = shutil.which("shutdown") or "shutdown"
            cmd = [shutdown_bin, "/r", "/t", "0"]
        else:
            reboot_bin = shutil.which("reboot") or "reboot"
            cmd = ["sudo", reboot_bin]
        self.process = subprocess.Popen(cmd)

    def shutdown(self) -> None:
        shutdown_bin = shutil.which("shutdown") or "shutdown"
        if self.os_type == "windows":
            cmd = [shutdown_bin, "/s", "/t", "0"]
        else:
            cmd = ["sudo", shutdown_bin, "-h", "now"]
        self.process = subprocess.Popen(cmd)


def setup_device(device_name: str, mac: str, ip: str, location: str, os_type: str, username: str = "", password: str = "") -> ConfigEntry:
    """Create a ConfigEntry and associated entities."""
    ipaddress.ip_address(ip)
    if device_name in _existing_devices:
        raise ValueError("Device name already exists")

    entry = ConfigEntry(
        device_name=device_name,
        mac=mac,
        ip=ip,
        location=location,
        os_type=os_type,
        username=username,
        password=password,
    )

    entry.add_entity(WakeOnLanSwitch(device_name, mac))
    entry.add_entity(PingBinarySensor(device_name, ip))
    entry.add_entity(SystemCommandSwitch(device_name, os_type, username, password))
    _existing_devices.add(device_name)
    return entry


def remove_device(entry: ConfigEntry) -> None:
    """Remove all entities associated with the config entry."""
    for ent in entry.entities:
        if isinstance(ent, SystemCommandSwitch) and ent.process and ent.process.poll() is None:
            ent.process.terminate()
            try:
                ent.process.wait(timeout=5)
            except Exception:
                pass
    entry.remove_entities()
    _existing_devices.discard(entry.device_name)
