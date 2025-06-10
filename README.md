# WoManager

A minimal Flask-based dashboard to manage Wake-on-LAN capable devices.

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Run the server:
   ```sh
   python wo_manager.py
   ```
   This will create a default `WoManager` dashboard if missing and start a web
   server on port 5000.

## Configuration

Edit `devices.json` to add or remove devices. Each device entry requires a
`name`, `mac`, and `ip` address.

Example:

```json
{
  "devices": [
    {"name": "Server", "mac": "00:11:22:33:44:55", "ip": "192.168.1.10"}
  ]
}
```

Changes to this file are reflected on the dashboard when the page reloads.

## Usage

The dashboard shows one card per device with buttons to wake, restart or shut
it down. Device online status is determined using a simple ping check when the
page loads.

Restart and shutdown actions attempt to run SSH commands on the device and may
require key-based authentication or additional configuration.
