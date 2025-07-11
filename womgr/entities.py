from dataclasses import dataclass, field
import asyncio
import logging
import socket
import subprocess
import sys
import shutil
from typing import List

logger = logging.getLogger(__name__)

from .util import parse_mac_address, slugify


def _create_entity_id(device_name: str, entity: str) -> str:
    """Generate a valid entity ID for a device."""
    name = slugify(device_name)
    return f"womgr_{name}_{entity}"


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
    color: str = ""
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

    def __init__(
        self,
        device_name: str,
        mac: str,
        broadcast: str = "<broadcast>",
        port: int = 9,
    ) -> None:
        super().__init__(device_name, "wol")
        self.mac = mac
        self.broadcast = broadcast
        self.port = port

    def turn_on(self) -> None:
        mac_bytes = parse_mac_address(self.mac)
        packet = b"\xff" * 6 + mac_bytes * 16
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(packet, (self.broadcast, self.port))
        except OSError as exc:
            logger = logging.getLogger(__name__)
            logger.error(
                "Failed to send WOL packet to %s:%s: %s",
                self.broadcast,
                self.port,
                exc,
            )


class PingBinarySensor(WoMgrEntity):
    """Binary sensor that checks reachability via ping."""

    def __init__(self, device_name: str, ip: str) -> None:
        super().__init__(device_name, "ping")
        self.ip = ip
        self.is_on = False

    def _build_ping_args(self) -> list[str]:
        ping_bin = shutil.which("ping") or "ping"
        args = [ping_bin]
        if sys.platform.startswith("win"):
            args += ["-n", "1", "-w", "1000", self.ip]
        else:
            args += ["-c", "1", "-W", "1", self.ip]
        return args

    async def update(self) -> bool:
        args = self._build_ping_args()
        try:
            proc = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.communicate()
            self.is_on = proc.returncode == 0
        except FileNotFoundError:
            self.is_on = False
        return self.is_on


class SystemCommandSwitch(WoMgrEntity):
    """Switch that issues restart or shutdown commands."""

    def __init__(
        self,
        device_name: str,
        os_type: str,
        username: str = "",
        password: str = "",
        shutdown_cmd: str | None = None,
        reboot_cmd: str | None = None,
    ) -> None:
        super().__init__(device_name, "system")
        self.os_type = os_type.lower()
        self.username = username
        self.password = password
        self.shutdown_cmd = shutdown_cmd
        self.reboot_cmd = reboot_cmd

    def _restart_command(self) -> list[str]:
        if self.os_type == "windows":

            shutdown_bin = shutil.which("shutdown")
            if shutdown_bin is None:
                raise FileNotFoundError("shutdown command not found")
            return [shutdown_bin, "/r", "/t", "0"]
        if self.os_type == "linux":
            reboot_bin = shutil.which("reboot")
            if reboot_bin is None:
                raise FileNotFoundError("reboot command not found")
            return ["sudo", reboot_bin]
        raise ValueError(f"Unsupported OS type: {self.os_type}")

    def _shutdown_command(self) -> list[str]:
        shutdown_bin = shutil.which("shutdown")
        if shutdown_bin is None:
            raise FileNotFoundError("shutdown command not found")
        if self.os_type == "windows":
            return [shutdown_bin, "/s", "/t", "0"]
        if self.os_type == "linux":
            return ["sudo", shutdown_bin, "-h", "now"]
        raise ValueError(f"Unsupported OS type: {self.os_type}")

    def restart(self) -> None:
        cmd = self._restart_command()
        subprocess.Popen(cmd)

    def shutdown(self) -> None:
        cmd = self._shutdown_command()
        subprocess.Popen(cmd)

    def available_commands(self) -> dict[str, bool]:
        if self.os_type == "windows":
            shutdown_bin = shutil.which("shutdown")
            return {"restart": shutdown_bin is not None, "shutdown": shutdown_bin is not None}
        if self.os_type == "linux":
            return {
                "restart": shutil.which("reboot") is not None,
                "shutdown": shutil.which("shutdown") is not None,
            }
        raise ValueError(f"Unsupported OS type: {self.os_type}")


def setup_device(
    device_name: str,
    mac: str,
    ip: str,
    location: str,
    os_type: str,
    username: str = "",
    password: str = "",
    color: str = "",
    broadcast: str = "<broadcast>",
    port: int = 9,
) -> ConfigEntry:
    """Create a ConfigEntry and associated entities.

    Wake-on-LAN packets use ``broadcast`` and ``port`` when initialized.
    """
    entry = ConfigEntry(
        device_name=device_name,
        mac=mac,
        ip=ip,
        location=location,
        os_type=os_type,
        username=username,
        password=password,
        color=color,
    )

    entry.add_entity(WakeOnLanSwitch(device_name, mac, broadcast, port))
    entry.add_entity(PingBinarySensor(device_name, ip))
    entry.add_entity(SystemCommandSwitch(device_name, os_type, username, password))
    return entry


def remove_device(entry: ConfigEntry) -> None:
    """Remove all entities associated with the config entry."""
    entry.remove_entities()
