"""API client for Kraichtal Wetter."""

from __future__ import annotations

from dataclasses import dataclass
import json
import logging
from typing import Any

from aiohttp import ClientError, ClientSession

from .const import ATTR_CURRENT_CONDITION, ATTR_FORECAST, ATTR_RADAR, BASE_URL
from .parsing import (
    derive_current_condition,
    last_chart_value,
    map_condition,
    parse_forecast,
    wind_bearing_from_text,
)

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class KraichtalWetterApiClient:
    """Simple API client for Kraichtal Wetter."""

    session: ClientSession
    base_url: str = BASE_URL

    async def async_fetch_all(
        self, include_forecast: bool, include_radar: bool
    ) -> dict[str, Any]:
        """Fetch current data plus optional forecast and radar data."""
        combined = await self._async_get_json("/api/combined.php")

        data: dict[str, Any] = dict(combined)
        if include_radar:
            try:
                data[ATTR_RADAR] = await self._async_get_json("/api/dwd_radar.php")
            except KraichtalWetterApiError as err:
                _LOGGER.warning("Could not update radar data: %s", err)
                data[ATTR_RADAR] = None

        if include_forecast:
            try:
                html = await self._async_get_text("/")
                data[ATTR_FORECAST] = parse_forecast(html, data.get("meta", {}))
            except KraichtalWetterApiError as err:
                _LOGGER.warning("Could not update homepage forecast: %s", err)
                data[ATTR_FORECAST] = []

        data[ATTR_CURRENT_CONDITION] = derive_current_condition(data)
        return data

    async def _async_get_json(self, path: str) -> dict[str, Any]:
        """Fetch JSON from the given path."""
        url = f"{self.base_url}{path}"
        try:
            async with self.session.get(url, timeout=15) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (ClientError, TimeoutError, ValueError) as err:
            raise KraichtalWetterApiError(f"Error fetching {url}") from err

        if not isinstance(payload, dict):
            raise KraichtalWetterApiError(f"Unexpected payload type from {url}")

        return payload

    async def _async_get_text(self, path: str) -> str:
        """Fetch text from the given path."""
        url = f"{self.base_url}{path}"
        try:
            async with self.session.get(url, timeout=15) as response:
                response.raise_for_status()
                return await response.text()
        except (ClientError, TimeoutError) as err:
            raise KraichtalWetterApiError(f"Error fetching {url}") from err


class KraichtalWetterApiError(Exception):
    """Raised when Kraichtal Wetter data cannot be loaded."""


def dump_forecast_debug(forecast: list[dict[str, Any]]) -> str:
    """Serialize forecast data for debugging."""
    return json.dumps(forecast, ensure_ascii=True)
