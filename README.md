# HaWoManager

HaWoManager is a lightweight Python tool to manage devices that support Wake-on-LAN (WOL). When you add a device, the manager automatically:

* Sends a WOL packet and checks that the device comes online. A log entry is created if it fails.
* Starts a background monitor to detect if the device goes offline unexpectedly.

Every wake, restart and shutdown action is written to `hawo.log` to make troubleshooting easier.

## Requirements

```bash
pip install -r requirements.txt
```

## Example

```python
from hawomanager import HaWoManager, Device

manager = HaWoManager()
device = Device(name="server", ip="192.168.1.100", mac="AA:BB:CC:DD:EE:FF")
manager.add_device(device)
manager.wake_device(device.name)
```
