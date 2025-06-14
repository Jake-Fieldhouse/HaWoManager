import argparse
import json
import requests
from womgr import pastel_color


def create_dashboard(url: str, token: str, device_name: str, color: str | None = None):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    # Fetch existing Lovelace config
    resp = requests.get(f"{url}/api/lovelace/config", headers=headers, timeout=10)
    resp.raise_for_status()
    config = resp.json()

    view = next((v for v in config.get("views", []) if v.get("path") == "womgr"), None)
    hash_tag = f"#womgr-{device_name}"
    color = color or pastel_color(device_name)
    card = {
        "type": "vertical-stack",
        "title": device_name,
        "cards": [
            {
                "type": "custom:bubble-card",
                "card_type": "pop-up",
                "hash": hash_tag,
                "cards": [
                    {"type": "entity", "entity": f"binary_sensor.{device_name}_ping"},
                    {"type": "entity", "entity": f"switch.{device_name}_wake"},
                    {"type": "button", "entity": f"button.{device_name}_restart"},
                    {"type": "button", "entity": f"button.{device_name}_shutdown"},
                ],
            },
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "name": device_name,
                "icon": "mdi:server-network",
                "tap_action": {"action": "navigate", "navigation_path": hash_tag},
                "show_state": False,
                "style": f"ha-card {{ background-color: {color}; }}",
            },
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
    parser.add_argument("--color", help="Bubble card background color", default=None)
    args = parser.parse_args()

    create_dashboard(args.url, args.token, args.device_name, args.color)


if __name__ == "__main__":
    main()
