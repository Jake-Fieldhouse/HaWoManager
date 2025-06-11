"""Button platform for WoMgr restart and shutdown actions."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity

from .const import DOMAIN
from .core.entities import SystemCommandSwitch


async def async_setup_entry(hass, entry, async_add_entities):
    config = hass.data[DOMAIN][entry.entry_id]
    systems = [e for e in config.entities if isinstance(e, SystemCommandSwitch)]
    buttons = []
    for system in systems:
        buttons.append(WoMgrRestartButton(system))
        buttons.append(WoMgrShutdownButton(system))
    async_add_entities(buttons)


class _SystemButton(ButtonEntity):
    def __init__(self, system: SystemCommandSwitch, action: str) -> None:
        self._system = system
        self._action = action
        self._attr_unique_id = f"{system.entity_id}_{action}"
        self._attr_name = f"{system.device_name} {action.title()}"


class WoMgrRestartButton(_SystemButton):
    def __init__(self, system: SystemCommandSwitch) -> None:
        super().__init__(system, "restart")

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._system.restart)


class WoMgrShutdownButton(_SystemButton):
    def __init__(self, system: SystemCommandSwitch) -> None:
        super().__init__(system, "shutdown")

    async def async_press(self) -> None:
        await self.hass.async_add_executor_job(self._system.shutdown)
