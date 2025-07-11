"""Switch platform for WoMgr (Wake-on-LAN)."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from womgr.entities import WakeOnLanSwitch


async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    switches = [e for e in config.entities if isinstance(e, WakeOnLanSwitch)]
    async_add_entities(WoMgrWakeSwitch(s) for s in switches)


class WoMgrWakeSwitch(SwitchEntity):
    """Switch that sends a Wake-on-LAN packet when turned on."""

    def __init__(self, switch: WakeOnLanSwitch) -> None:
        self._switch = switch
        self._attr_unique_id = switch.entity_id
        self._attr_name = f"{switch.device_name} Wake"
        self._attr_is_on = False

    async def async_turn_on(self, **kwargs) -> None:
        await self.hass.async_add_executor_job(self._switch.turn_on)
        self._attr_is_on = False
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        return
