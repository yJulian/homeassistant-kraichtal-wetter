"""Config flow for the Kraichtal Wetter integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_INCLUDE_FORECAST,
    CONF_INCLUDE_RADAR,
    CONF_SCAN_INTERVAL,
    DEFAULT_INCLUDE_FORECAST,
    DEFAULT_INCLUDE_RADAR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MAX_SCAN_INTERVAL,
    MIN_SCAN_INTERVAL,
    NAME,
)


def _schema_with_defaults(options: dict[str, Any]) -> vol.Schema:
    """Build the config schema with defaults from data or options."""
    return vol.Schema(
        {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)),
            vol.Optional(
                CONF_INCLUDE_FORECAST,
                default=options.get(CONF_INCLUDE_FORECAST, DEFAULT_INCLUDE_FORECAST),
            ): bool,
            vol.Optional(
                CONF_INCLUDE_RADAR,
                default=options.get(CONF_INCLUDE_RADAR, DEFAULT_INCLUDE_RADAR),
            ): bool,
        }
    )


class KraichtalWetterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Kraichtal Wetter."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=NAME, data=user_input)

        return self.async_show_form(step_id="user", data_schema=_schema_with_defaults({}))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow handler."""
        return KraichtalWetterOptionsFlow(config_entry)


class KraichtalWetterOptionsFlow(OptionsFlow):
    """Handle options for Kraichtal Wetter."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(
            step_id="init",
            data_schema=_schema_with_defaults(options),
        )
