"""Ping binary sensor platform for WoMgr."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN
from .womgr.entities import PingBinarySensor


async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    sensors = [e for e in config.entities if isinstance(e, PingBinarySensor)]
    async_add_entities(WoMgrPingBinarySensor(s) for s in sensors)


class WoMgrPingBinarySensor(BinarySensorEntity):
    """Binary sensor that wraps PingBinarySensor."""

    def __init__(self, sensor: PingBinarySensor) -> None:
        self._sensor = sensor
        self._attr_unique_id = sensor.entity_id
        self._attr_name = f"{sensor.device_name} Ping"

    async def async_update(self) -> None:
        await self._sensor.update()

    @property
    def is_on(self) -> bool:
        return self._sensor.is_on
