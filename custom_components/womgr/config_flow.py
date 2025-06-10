"""Config flow for the WoMgr integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN


class WoMgrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WoMgr."""

    VERSION = 2

    async def async_step_user(self, user_input: dict | None = None):
        """Initial step for integration setup."""
        base_exists = any(not entry.data for entry in self._async_current_entries())

        if not base_exists:
            if user_input is not None:
                if not user_input.get("add_device"):
                    await self.async_set_unique_id(DOMAIN)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title="HaWoManager", data={})
                return await self.async_step_device()

            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({vol.Optional("add_device", default=False): bool}),
            )

        return await self.async_step_device(user_input)

    async def async_step_device(self, user_input: dict | None = None):
        """Collect device information to create a config entry."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input["device_name"],
                data=user_input,
            )

        data_schema = vol.Schema(
            {
                vol.Required("device_name"): str,
                vol.Required("mac"): str,
                vol.Required("ip"): str,
                vol.Required("location"): str,
                vol.Required("os_type", default="linux"): vol.In(["linux", "windows"]),
                vol.Optional("username", default=""): str,
                vol.Optional("password", default=""): str,
            }
        )

        return self.async_show_form(step_id="device", data_schema=data_schema)
