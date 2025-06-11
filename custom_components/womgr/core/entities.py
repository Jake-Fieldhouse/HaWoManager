from dataclasses import dataclass, field
import socket
import subprocess
import sys
from typing import List

from ..util import parse_mac_address


def _create_entity_id(device_name: str, entity: str) -> str:
    return f"womgr_{device_name}_{entity}"


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

    def restart(self) -> None:
        if self.os_type == "windows":
            cmd = ["shutdown", "/r", "/t", "0"]
        else:
            cmd = ["sudo", "reboot"]
        subprocess.Popen(cmd)

    def shutdown(self) -> None:
        if self.os_type == "windows":
            cmd = ["shutdown", "/s", "/t", "0"]
        else:
            cmd = ["sudo", "shutdown", "-h", "now"]
        subprocess.Popen(cmd)


def setup_device(device_name: str, mac: str, ip: str, location: str, os_type: str, username: str = "", password: str = "") -> ConfigEntry:
    """Create a ConfigEntry and associated entities."""
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
    return entry


def remove_device(entry: ConfigEntry) -> None:
    """Remove all entities associated with the config entry."""
    entry.remove_entities()
