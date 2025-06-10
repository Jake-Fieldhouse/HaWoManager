import logging
import subprocess
import threading
import time
from dataclasses import dataclass
from typing import Dict

from wakeonlan import send_magic_packet


@dataclass
class Device:
    name: str
    ip: str
    mac: str
    online: bool = False


class HaWoManager:
    """Simple manager for wake on LAN devices."""

    def __init__(self, log_file: str = "hawo.log"):
        logging.basicConfig(
            filename=log_file,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s",
        )
        self.devices: Dict[str, Device] = {}
        self.monitors: Dict[str, threading.Thread] = {}

    def add_device(self, device: Device) -> None:
        """Add a device and start offline monitoring."""
        self.devices[device.name] = device
        logging.info("Added device %s (%s)", device.name, device.ip)
        monitor = threading.Thread(target=self._monitor_device, args=(device,), daemon=True)
        monitor.start()
        self.monitors[device.name] = monitor

    def _monitor_device(self, device: Device) -> None:
        """Monitor device connectivity."""
        while True:
            is_up = self._ping(device.ip)
            if device.online and not is_up:
                logging.warning("Device %s went offline unexpectedly", device.name)
            device.online = is_up
            time.sleep(60)

    def _ping(self, ip: str) -> bool:
        result = subprocess.run(["ping", "-c", "1", ip], stdout=subprocess.DEVNULL)
        return result.returncode == 0

    def wake_device(self, name: str) -> None:
        device = self.devices.get(name)
        if not device:
            raise ValueError(f"Device '{name}' not found")
        logging.info("Sending WOL to %s", name)
        send_magic_packet(device.mac)
        # check if device comes online within 60 seconds
        for _ in range(12):
            if self._ping(device.ip):
                device.online = True
                logging.info("Device %s came online", name)
                break
            time.sleep(5)
        else:
            logging.error("Device %s did not come online after WOL", name)

    def restart_device(self, name: str) -> None:
        device = self.devices.get(name)
        if not device:
            raise ValueError(f"Device '{name}' not found")
        logging.info("Restarting %s", name)
        # Placeholder for actual restart logic

    def shutdown_device(self, name: str) -> None:
        device = self.devices.get(name)
        if not device:
            raise ValueError(f"Device '{name}' not found")
        logging.info("Shutting down %s", name)
        # Placeholder for actual shutdown logic


def main() -> None:
    manager = HaWoManager()
    # Example usage
    device = Device(name="server", ip="192.168.1.100", mac="AA:BB:CC:DD:EE:FF")
    manager.add_device(device)
    manager.wake_device(device.name)


if __name__ == "__main__":
    main()
