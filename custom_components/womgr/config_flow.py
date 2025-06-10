"""Config flow for the WoMgr integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from .const import DOMAIN


    """Handle a config flow for WoMgr."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None):
        """Handle the initial step."""
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

        return self.async_show_form(step_id="user", data_schema=data_schema)
