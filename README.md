# HaWoManager

This repository provides a minimal set of helpers for managing devices with a
consistent entity naming scheme.  The module exposes simple classes to:

* Send Wake-on-LAN packets to a device via a `WakeOnLanSwitch`.
* Check device reachability with a `PingBinarySensor`.
* Issue restart and shutdown commands using `SystemCommandSwitch`.

Entities are grouped by `ConfigEntry` instances so they can be created and
removed together.  Each entity uses the naming scheme
`womgr_{device_name}_{entity}` for its `entity_id`.

```
from womgr import setup_device, remove_device

entry = setup_device(
    device_name="server", mac="00:11:22:33:44:55", ip="192.0.2.10", os_type="linux"
)
# entry.entities now contains WakeOnLanSwitch, PingBinarySensor and SystemCommandSwitch

# later
remove_device(entry)
```
