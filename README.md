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

The installation pulls in the `requests` package, which is required for the
`dashboard_cli.py` helper script.

Alternatively, install directly from GitHub:

```bash
pip install git+https://github.com/example/HaWoManager.git
```

### HACS Installation

Add this repository as a custom repository in HACS if you prefer managing
updates from the Home Assistant UI:

1. Open **HACS** in Home Assistant and choose **Integrations**.
2. Click the three‑dot menu and select **Custom Repositories**.
3. Enter the repository URL `https://github.com/example/HaWoManager` and set the
   category to **Integration**.
4. HACS installs only from tagged releases. Ensure you select the latest release
   rather than a specific commit.
5. After adding the repository, search for **WoMgr** under Integrations and
   install it. Restart Home Assistant when prompted.
6. Finally, add the **WoMgr** integration from the Integrations page as usual.

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

### CLI Usage

For simple one-off commands you can use `womgr_cli.py`:

```bash
python womgr_cli.py DEVICE_NAME AA:BB:CC:DD:EE:FF 192.0.2.10 Office linux ping
```
The command arguments are `DEVICE_NAME` `MAC` `IP` `LOCATION` `OS_TYPE` and the desired action.

The last argument chooses the action: `wol`, `ping`, `restart`, `shutdown`, or
`status`. Credentials for system commands can be provided with `--username` and
`--password` options. The ping command automatically adjusts parameters for Windows or Linux hosts.

Example to check both reachability and command availability:

```bash
python womgr_cli.py DEVICE_NAME AA:BB:CC:DD:EE:FF 192.0.2.10 Office linux status
```

## Home Assistant Integration

Copy the `custom_components/womgr` folder into your Home Assistant `config/custom_components` directory and restart Home Assistant.  Add the **WoMgr** integration from the Integrations page.  The initial setup can be completed without specifying a device so you may install the integration first and add devices later.  Simply run **Add Integration** again for each machine you want to manage and enter its name, MAC address, IP, location and operating system.  Username and password remain optional and are only needed for restart or shutdown commands.  When the first device is added, the integration creates a **HaWoManager** dashboard and inserts a Bubble Card for the device.  Additional devices are appended to the same dashboard automatically. You may also set a pastel color for the device's button.

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

### Automatic Dashboard Setup

The integration automatically manages a dashboard named **HaWoManager**.  Each
device you add is placed on this dashboard as a Bubble Card.  If you prefer to
manage the dashboard outside Home Assistant or need to recreate it, you can use
the `dashboard_cli.py` utility.  The script calls the Home Assistant REST API to
create the view and insert the card.  Provide your Home Assistant URL and a
long-lived access token:

```bash
python dashboard_cli.py http://homeassistant.local:8123 YOUR_TOKEN server
```

Add `--color` to pick a custom pastel color for the device's button:

```bash
python dashboard_cli.py http://homeassistant.local:8123 YOUR_TOKEN server --color "rgb(200, 230, 255)"
```

Repeat the command for additional devices. The script appends a card to the
`HaWoManager` view each time it runs.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release notes. The latest release is **v0.0.6**.
