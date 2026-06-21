"""Data coordinator for Kraichtal Wetter."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import KraichtalWetterApiClient, KraichtalWetterApiError
from .const import (
    CONF_INCLUDE_FORECAST,
    CONF_INCLUDE_RADAR,
    CONF_SCAN_INTERVAL,
    DEFAULT_INCLUDE_FORECAST,
    DEFAULT_INCLUDE_RADAR,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class KraichtalWetterCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate data updates for Kraichtal Wetter."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize coordinator."""
        self.config_entry = entry
        self.api = KraichtalWetterApiClient(async_get_clientsession(hass))
        interval = entry.options.get(
            CONF_SCAN_INTERVAL,
            entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
        )
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the remote API."""
        include_forecast = self.config_entry.options.get(
            CONF_INCLUDE_FORECAST,
            self.config_entry.data.get(CONF_INCLUDE_FORECAST, DEFAULT_INCLUDE_FORECAST),
        )
        include_radar = self.config_entry.options.get(
            CONF_INCLUDE_RADAR,
            self.config_entry.data.get(CONF_INCLUDE_RADAR, DEFAULT_INCLUDE_RADAR),
        )

        try:
            return await self.api.async_fetch_all(include_forecast, include_radar)
        except KraichtalWetterApiError as err:
            raise UpdateFailed(str(err)) from err
