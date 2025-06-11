"""WoMgr integration initialization."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.components.lovelace.const import (
    CONF_ALLOW_SINGLE_WORD,
    CONF_ICON,
    CONF_TITLE,
    CONF_URL_PATH,
)
from homeassistant.components.lovelace.dashboard import (
    DashboardsCollection,
    LovelaceStorage,
    ConfigNotFound,
)

from .core import setup_device, remove_device

from .const import DOMAIN

PLATFORMS: list[str] = ["switch", "binary_sensor", "button"]


async def _async_update_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ensure a HaWoManager dashboard exists and contains the device card."""
    if not entry.data:
        return
    lovelace = hass.data.get("lovelace")
    if not lovelace:
        return

    dashboards: dict = lovelace.get("dashboards", {})
    dashboards_collection: DashboardsCollection = lovelace.get("dashboards_collection")

    if dashboards_collection is None:
        return

    if "womgr" not in dashboards:
        await dashboards_collection.async_create_item(
            {
                CONF_ALLOW_SINGLE_WORD: True,
                CONF_ICON: "mdi:server-network",
                CONF_TITLE: "HaWoManager",
                CONF_URL_PATH: "womgr",
            }
        )

    dashboard: LovelaceStorage = dashboards["womgr"]

    try:
        config = await dashboard.async_load(False)
    except ConfigNotFound:
        config = {"views": []}


    view = next((v for v in config.get("views", []) if v.get("path") == "womgr"), None)
    hash_tag = f"#womgr-{entry.data['device_name']}"
    card = {
        "type": "vertical-stack",
        "title": entry.data["device_name"],
        "cards": [
            {
                "type": "custom:bubble-card",
                "card_type": "pop-up",
                "hash": hash_tag,
                "cards": [
                    {"type": "entity", "entity": f"binary_sensor.{entry.data['device_name']}_ping"},
                    {"type": "entity", "entity": f"switch.{entry.data['device_name']}_wake"},
                    {"type": "button", "entity": f"button.{entry.data['device_name']}_restart"},
                    {"type": "button", "entity": f"button.{entry.data['device_name']}_shutdown"},
                ],
            },
            {
                "type": "custom:bubble-card",
                "card_type": "button",
                "name": entry.data["device_name"],
                "icon": "mdi:server-network",
                "tap_action": {"action": "navigate", "navigation_path": hash_tag},
                "show_state": False,
            },
        ],
    }

    if view is None:
        view = {"path": "womgr", "title": "HaWoManager", "cards": [card]}
        config.setdefault("views", []).append(view)
    else:
        view.setdefault("cards", [])
        if not any(c.get("title") == entry.data["device_name"] for c in view["cards"]):
            view["cards"].append(card)

    await dashboard.async_save(config)


async def _async_remove_dashboard_card(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the card for a device when the entry is unloaded."""
    if not entry.data:
        return
    lovelace = hass.data.get("lovelace")
    if not lovelace:
        return

    dashboards: dict = lovelace.get("dashboards", {})
    if "womgr" not in dashboards:
        return

    dashboard: LovelaceStorage = dashboards["womgr"]

    try:
        config = await dashboard.async_load(False)
    except ConfigNotFound:
        return

    view = next((v for v in config.get("views", []) if v.get("path") == "womgr"), None)
    if view is None:
        return

    cards = view.get("cards", [])
    view["cards"] = [c for c in cards if c.get("title") != entry.data["device_name"]]

    await dashboard.async_save(config)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the WoMgr component from YAML."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WoMgr from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    if not entry.data:
        # Base configuration entry, nothing to set up yet
        return True

    hass.data[DOMAIN][entry.entry_id] = setup_device(**entry.data)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.async_create_task(_async_update_dashboard(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a WoMgr config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    config = hass.data[DOMAIN].pop(entry.entry_id, None)
    if config:
        remove_device(config)
        await _async_remove_dashboard_card(hass, entry)
    return True
