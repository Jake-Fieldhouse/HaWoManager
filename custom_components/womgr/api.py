from __future__ import annotations

import asyncio
from typing import Any

from homeassistant.components.http import HomeAssistantView
from homeassistant.core import HomeAssistant

from .const import DOMAIN


class DevicesView(HomeAssistantView):
    """View to list and control WoMgr devices."""

    url = "/api/womgr/devices"
    name = "api:womgr:devices"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def get(self, request):
        data = []
        for entry_id, config in self.hass.data.get(DOMAIN, {}).items():
            device = {
                "entry_id": entry_id,
                "device_name": config.device_name,
                "mac": config.mac,
                "ip": config.ip,
                "os_type": config.os_type,
            }
            for entity in config.entities:
                if entity.entity_id.endswith("_ping"):
                    device["online"] = entity.is_on
            data.append(device)
        return self.json(data)

    async def post(self, request):
        body: dict[str, Any] = await request.json()
        entry_id = body.get("entry_id")
        action = body.get("action")
        if not entry_id or not action:
            return self.json({"error": "missing parameters"}, status_code=400)
        config = self.hass.data.get(DOMAIN, {}).get(entry_id)
        if not config:
            return self.json({"error": "unknown device"}, status_code=404)
        if action == "wake":
            wol = next(e for e in config.entities if e.entity_id.endswith("_wol"))
            for _ in range(3):
                await self.hass.async_add_executor_job(wol.turn_on)
                await asyncio.sleep(1)
        elif action in ("restart", "shutdown"):
            sys_entity = next(
                e for e in config.entities if e.entity_id.endswith("_system")
            )
            func = getattr(sys_entity, action)
            await self.hass.async_add_executor_job(func)
        elif action == "refresh":
            ping = next(e for e in config.entities if e.entity_id.endswith("_ping"))
            await ping.update()
        else:
            return self.json({"error": "unknown action"}, status_code=400)
        return self.json({"success": True})


class ExportView(HomeAssistantView):
    url = "/api/womgr/export"
    name = "api:womgr:export"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def get(self, request):
        entries = [entry.data for entry in self.hass.config_entries.async_entries(DOMAIN) if entry.data]
        return self.json(entries)


class ImportView(HomeAssistantView):
    url = "/api/womgr/import"
    name = "api:womgr:import"
    requires_auth = True

    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass

    async def post(self, request):
        devices: list[dict[str, Any]] = await request.json()
        flow = self.hass.config_entries.flow
        for dev in devices:
            await flow.async_init(DOMAIN, context={"source": "user"}, data=dev)
        return self.json({"success": True})
