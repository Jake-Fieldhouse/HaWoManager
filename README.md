# HaWoManager

This repository contains a custom Home Assistant integration called **WO Manager**. It includes a configuration flow that guides you through adding devices from Home Assistant's UI.

## Usage

Copy the `custom_components/womgr` folder to your Home Assistant `custom_components` directory. Restart Home Assistant and use **Add Device** from the integrations page to register a new machine. You will be asked for:

- Device name
- MAC address
- IP address
- Operating system type
- Credentials method (password or SSH key)

The information is stored in Home Assistant's configuration entries for later use.
