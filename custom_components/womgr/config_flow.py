"""Config flow for womgr integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from . import DOMAIN


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for womgr."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            self._data.update(user_input)
            return await self._async_create_entry()

        schema = vol.Schema(
            {
                vol.Required("device_name"): str,
                vol.Required("mac_address"): str,
                vol.Required("ip_address"): str,
                vol.Required("os_type"): vol.In(["Windows", "Linux", "macOS", "Other"]),
                vol.Required("credentials_method"): vol.In(["password", "ssh_key"]),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema)

    async def _async_create_entry(self) -> FlowResult:
        """Create the config entry."""
        return self.async_create_entry(title=self._data["device_name"], data=self._data)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""

        class OptionsFlowHandler(config_entries.OptionsFlow):
            """Handle options."""

            def __init__(self, entry: config_entries.ConfigEntry) -> None:
                self.entry = entry
                self._options = dict(entry.data)

            async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
                if user_input is not None:
                    self._options.update(user_input)
                    return self.async_create_entry(title="Options", data=self._options)

                schema = vol.Schema(
                    {
                        vol.Required(
                            "credentials_method",
                            default=self._options.get("credentials_method", "password"),
                        ): vol.In(["password", "ssh_key"]),
                    }
                )

                return self.async_show_form(step_id="init", data_schema=schema)

        return OptionsFlowHandler(config_entry)
