import argparse
import json
import os
import requests
from requests import RequestException


def create_dashboard(
    url: str, token: str, device_name: str, path: str = "womgr"
) -> None:
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        resp = requests.get(f"{url}/api/lovelace/config", headers=headers, timeout=10)
        resp.raise_for_status()
        config = resp.json()
    except RequestException as exc:
        print(f"Failed to fetch Lovelace config: {exc}")
        return

    view = next((v for v in config.get("views", []) if v.get("path") == path), None)
    hash_tag = f"#{path}-{device_name}"
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
            },
        ],
    }

    if view is None:
        view = {"path": path, "title": "HaWoManager", "cards": [card]}
        config.setdefault("views", []).append(view)
    else:
        view.setdefault("cards", []).append(card)

    try:
        resp = requests.post(
            f"{url}/api/lovelace/config",
            headers=headers,
            data=json.dumps(config),
            timeout=10,
        )
        resp.raise_for_status()
    except RequestException as exc:
        print(f"Failed to update Lovelace config: {exc}")


def main():
    parser = argparse.ArgumentParser(description="Create HaWoManager dashboard")
    parser.add_argument("url", help="Base URL of Home Assistant, e.g. http://hass:8123")
    parser.add_argument("device_name", help="Device name used in HaWoManager")
    parser.add_argument(
        "--token",
        help="Long-Lived Access Token; falls back to HASS_TOKEN environment variable",
    )
    parser.add_argument(
        "--path",
        default="womgr",
        help="Dashboard URL path to use (default: womgr)",
    )
    args = parser.parse_args()

    token = args.token or os.environ.get("HASS_TOKEN")
    if not token:
        parser.error(
            "Token must be provided via --token or HASS_TOKEN environment variable"
        )

    create_dashboard(args.url, token, args.device_name, args.path)


if __name__ == "__main__":
    main()
