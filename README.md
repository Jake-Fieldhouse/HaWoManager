# HaWoManager

HaWoManager is a Home Assistant integration for managing network devices using Wake-on-LAN and optional restart or shutdown commands. It automatically creates a dedicated dashboard so your devices appear with status and controls.

Entities created by the utilities follow the naming scheme
`womgr_{device_name}_{entity}` so they can easily be grouped by device.

## Installation

### Install via HACS (recommended)

1. Open **HACS** in Home Assistant and choose **Integrations**.
2. Click the three-dot menu and select **Custom Repositories**.
3. Enter `https://github.com/example/HaWoManager` and set the category to **Integration**.
4. After adding the repository, search for **WoMgr** under Integrations and install it.
   Restart Home Assistant when prompted.



## Home Assistant Integration
After installing via HACS, add the **WoMgr** integration from the Integrations page. The initial setup can be completed without specifying a device so you may install the integration first and add devices later. Simply run **Add Integration** again for each machine you want to manage and enter its name, MAC address, IP, location and operating system. Username and password remain optional and are only needed for restart or shutdown commands. You can also provide a custom dashboard or view name instead of the default `womgr`. When the first device is added, the integration creates a **HaWoManager** dashboard and inserts a Bubble Card for the device. Additional devices are appended to the chosen dashboard automatically. You may also set a pastel color for the device's button.

## Usage

```python
from womgr import setup_device, remove_device

entry = setup_device(
    device_name="server",
    mac="00:11:22:33:44:55",
    ip="192.0.2.10",
    location="Office",
    os_type="linux",
    color="rgb(200, 230, 255)",
)
# entry.entities now contains WakeOnLanSwitch,
# PingBinarySensor and SystemCommandSwitch

# later when the device should be removed
remove_device(entry)
```

Wake-on-LAN packets are sent to `<broadcast>` on UDP port `9` by default.
Use the optional `broadcast` and `port` arguments of `setup_device()` to
override these values.
The `color` argument lets you pick a pastel background for the Bubble Card button.


## Home Assistant Integration

After installing via HACS, add the **WoMgr** integration from the Integrations page.  The initial setup can be completed without specifying a device so you may install the integration first and add devices later.  Simply run **Add Integration** again for each machine you want to manage and enter its name, MAC address, IP, location and operating system.  Username and password remain optional and are only needed for restart or shutdown commands.  You can also provide a custom dashboard or view name instead of the default `womgr`.  When the first device is added, the integration creates a **HaWoManager** dashboard and inserts a Bubble Card for the device.  Additional devices are appended to the chosen dashboard automatically. You may also set a pastel color for the device's button.


### Example Dashboard

Below is a minimal example using the community "Bubble Card".  An example file is provided at `lovelace/womgr_example.yaml`.  Import it into your dashboard or copy the following snippet:

```yaml

type: vertical-stack
title: HaWoManager
cards:
  - type: custom:bubble-card
    card_type: pop-up
    hash: '#server'
    cards:
      - type: entity
        entity: binary_sensor.server_ping
      - type: entity
        entity: switch.server_wake
      - type: button
        entity: button.server_restart
      - type: button
        entity: button.server_shutdown
  - type: custom:bubble-card
    card_type: button
    name: Server
    icon: mdi:server-network
    tap_action:
      action: navigate
      navigation_path: '#server'
    show_state: false
    style: |
      ha-card {
        background-color: rgb(200, 230, 255);
      }
```

This example assumes the device was added with the name `server`.


## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes. The latest release is **v0.0.9**.
