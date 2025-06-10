# HaWoManager

HaWoManager is a small collection of helpers for managing network devices with
Home Assistant or stand‑alone Python scripts.  It provides simple classes to
send Wake‑on‑LAN packets, check device availability via ping and issue restart
or shutdown commands.

Entities created by the utilities follow the naming scheme
`womgr_{device_name}_{entity}` so they can easily be grouped by device.

## Installation

Clone the repository and install it with `pip`:

```bash
git clone https://github.com/example/HaWoManager.git
cd HaWoManager
pip install .
```

Alternatively, install directly from GitHub:

```bash
pip install git+https://github.com/example/HaWoManager.git
```

## Usage

```python
from womgr import setup_device, remove_device

entry = setup_device(
    device_name="server",
    mac="00:11:22:33:44:55",
    ip="192.0.2.10",
    os_type="linux",
)
# entry.entities now contains WakeOnLanSwitch,
# PingBinarySensor and SystemCommandSwitch

# later when the device should be removed
remove_device(entry)
```
