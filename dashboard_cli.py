import argparse
import json
import requests


def create_dashboard(url: str, token: str, device_name: str):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Fetch existing Lovelace config
    resp = requests.get(f"{url}/api/lovelace/config", headers=headers, timeout=10)
    resp.raise_for_status()
    config = resp.json()

    view = next((v for v in config.get("views", []) if v.get("path") == "womgr"), None)
    card = {
        "type": "custom:bubble-card",
        "title": "HaWoManager",
        "cards": [
            {"type": "entity", "entity": f"binary_sensor.{device_name}_ping"},
            {"type": "entity", "entity": f"switch.{device_name}_wake"},
            {"type": "button", "entity": f"button.{device_name}_restart"},
            {"type": "button", "entity": f"button.{device_name}_shutdown"},
        ],
    }

    if view is None:
        view = {"path": "womgr", "title": "HaWoManager", "cards": [card]}
        config.setdefault("views", []).append(view)
    else:
        view.setdefault("cards", []).append(card)

    resp = requests.post(
        f"{url}/api/lovelace/config",
        headers=headers,
        data=json.dumps(config),
        timeout=10,
    )
    resp.raise_for_status()


def main():
    parser = argparse.ArgumentParser(description="Create HaWoManager dashboard")
    parser.add_argument("url", help="Base URL of Home Assistant, e.g. http://hass:8123")
    parser.add_argument("token", help="Long-Lived Access Token")
    parser.add_argument("device_name", help="Device name used in HaWoManager")
    args = parser.parse_args()

    create_dashboard(args.url, args.token, args.device_name)


if __name__ == "__main__":
    main()
