"""WoMgr integration initialization."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
import asyncio
import os
from homeassistant.components.lovelace.const import (
    CONF_ALLOW_SINGLE_WORD,
    CONF_ICON,
    CONF_TITLE,
    CONF_URL_PATH,
)
from homeassistant.components.http import StaticPathConfig
from .api import DevicesView, ExportView, ImportView
from homeassistant.components.lovelace.dashboard import (
    DashboardsCollection,
    LovelaceStorage,
)
from homeassistant.helpers import device_registry as dr

from .core import setup_device, remove_device
from .womgr import pastel_color

from .const import DOMAIN

PLATFORMS: list[str] = ["switch", "binary_sensor", "button"]


# Lock used to serialize dashboard modifications
_dashboard_lock = asyncio.Lock()


async def _async_update_dashboard(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Ensure a HaWoManager dashboard exists and contains the device card."""
    if not entry.data:
        return
    lovelace = hass.data.get("lovelace")
    if not lovelace:
        return

    from homeassistant.components.lovelace.dashboard import ConfigNotFound

    dashboards: dict = getattr(lovelace, "dashboards", lovelace.get("dashboards", {}))
    dashboards_collection: DashboardsCollection = getattr(
        lovelace, "dashboards_collection", lovelace.get("dashboards_collection")
    )

    if dashboards_collection is None:
        return

    view_path = entry.data.get("dashboard") or "womgr"

    async with _dashboard_lock:
        if view_path not in dashboards:
            await dashboards_collection.async_create_item(
                {
                    CONF_ALLOW_SINGLE_WORD: True,
                    CONF_ICON: "mdi:server-network",
                    CONF_TITLE: "HaWoManager",
                    CONF_URL_PATH: view_path,
                }
            )

        dashboard: LovelaceStorage = dashboards[view_path]

        try:
            config = await dashboard.async_load(False)
        except Exception as exc:  # ConfigNotFound in tests
            if exc.__class__.__name__ == "ConfigNotFound":
                config = {"views": []}
            else:
                raise

        view = next((v for v in config.get("views", []) if v.get("path") == view_path), None)
        color = entry.data.get("color") or pastel_color(entry.data["device_name"])
        hash_tag = f"#{view_path}-{entry.data['device_name']}"
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
                    **({"style": f"ha-card {{ background-color: {color}; }}"}),
                },
            ],
        }

        if view is None:
            view = {"path": view_path, "title": "HaWoManager", "cards": [card]}
            config.setdefault("views", []).append(view)
        else:
            view.setdefault("cards", [])
            for idx, existing in enumerate(view["cards"]):
                if existing.get("title") == entry.data["device_name"]:
                    view["cards"][idx] = card
                    break
            else:
                view["cards"].append(card)

        await dashboard.async_save(config)


async def _async_remove_dashboard_card(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove the card for a device when the entry is unloaded."""
    if not entry.data:
        return
    lovelace = hass.data.get("lovelace")
    if not lovelace:
        return

    from homeassistant.components.lovelace.dashboard import ConfigNotFound

    dashboards: dict = getattr(lovelace, "dashboards", lovelace.get("dashboards", {}))
    view_path = entry.data.get("dashboard") or "womgr"
    if view_path not in dashboards:
        return

    async with _dashboard_lock:
        dashboard: LovelaceStorage = dashboards[view_path]

        try:
            config = await dashboard.async_load(False)
        except Exception as exc:  # ConfigNotFound in tests
            if exc.__class__.__name__ == "ConfigNotFound":
                return
            raise

        view = next((v for v in config.get("views", []) if v.get("path") == view_path), None)
        if view is None:
            return

        cards = view.get("cards", [])
        view["cards"] = [c for c in cards if c.get("title") != entry.data["device_name"]]

        await dashboard.async_save(config)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the WoMgr component from YAML."""
    hass.data.setdefault(DOMAIN, {})

    panel_path = os.path.join(os.path.dirname(__file__), "www", "panel.html")
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/womgr-panel", panel_path, False)]
    )
    from homeassistant.components import frontend

    frontend.async_register_built_in_panel(
        hass,
        "iframe",
        "HaWoManager",
        "mdi:server-network",
        "womgr",
        {"url": "/womgr-panel"},
        require_admin=True,
    )
    hass.http.register_view(DevicesView(hass))
    hass.http.register_view(ExportView(hass))
    hass.http.register_view(ImportView(hass))
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WoMgr from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    if not entry.data:
        # Base configuration entry, nothing to set up yet
        return True

    setup_args = {k: v for k, v in entry.data.items() if k != "dashboard"}
    hass.data[DOMAIN][entry.entry_id] = setup_device(**setup_args)
    dev_reg = dr.async_get(hass)
    device = dev_reg.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.entry_id)},
        name=entry.data.get("device_name"),
        manufacturer="HaWoManager",
        model=entry.data.get("os_type"),
    )
    if area := entry.data.get("area"):
        dev_reg.async_update_device(device.id, area_id=area)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    hass.async_create_task(_async_update_dashboard(hass, entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a WoMgr config entry."""
    if entry.data:
        await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    config = hass.data[DOMAIN].pop(entry.entry_id, None)
    if config:
        remove_device(config)
        await _async_remove_dashboard_card(hass, entry)
    return True
