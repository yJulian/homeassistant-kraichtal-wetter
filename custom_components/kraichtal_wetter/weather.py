"""Weather platform for Kraichtal Wetter."""

from __future__ import annotations

from typing import Any

from homeassistant.components.weather import WeatherEntity, WeatherEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfLength,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import last_chart_value, wind_bearing_from_text
from .const import ATTR_FORECAST, ATTR_RADAR, DOMAIN, NAME
from .coordinator import KraichtalWetterCoordinator
from .entity import KraichtalWetterEntity
from .parsing import build_daily_forecast


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the weather entity from config entry."""
    coordinator: KraichtalWetterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([KraichtalWeatherEntity(coordinator)])


class KraichtalWeatherEntity(KraichtalWetterEntity, WeatherEntity):
    """Representation of Kraichtal Wetter as a weather entity."""

    _attr_name = NAME
    _attr_unique_id = f"{DOMAIN}_weather"
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_native_precipitation_unit = UnitOfLength.MILLIMETERS

    @property
    def supported_features(self) -> WeatherEntityFeature:
        """Return supported weather features."""
        if self.forecast_daily:
            return WeatherEntityFeature.FORECAST_DAILY
        return WeatherEntityFeature(0)

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        return (self.coordinator.data or {}).get("current_condition")

    @property
    def native_temperature(self) -> float | None:
        """Return the current temperature."""
        return _current(self.coordinator.data, "temp")

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature."""
        return _current(self.coordinator.data, "feelsLike")

    @property
    def native_dew_point(self) -> float | None:
        """Return the dew point."""
        return _current(self.coordinator.data, "dewpoint")

    @property
    def humidity(self) -> int | None:
        """Return current humidity."""
        return _current(self.coordinator.data, "humidity")

    @property
    def native_pressure(self) -> float | None:
        """Return current pressure."""
        return _current(self.coordinator.data, "pressure")

    @property
    def native_wind_speed(self) -> float | None:
        """Return current wind speed."""
        return _current(self.coordinator.data, "wind")

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return latest wind gust speed from the chart data."""
        chart_gust = ((self.coordinator.data or {}).get("charts") or {}).get("wind", {}).get("gust")
        return last_chart_value(chart_gust)

    @property
    def wind_bearing(self) -> float | None:
        """Return wind bearing in degrees."""
        return wind_bearing_from_text(_current(self.coordinator.data, "windDir"))

    @property
    async def async_forecast_daily(self) -> list[dict[str, Any]] | None:
        """Return daily forecast data."""
        forecast = (self.coordinator.data or {}).get(ATTR_FORECAST)
        return build_daily_forecast(forecast)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional metadata for debugging and diagnostics."""
        data = self.coordinator.data or {}
        attrs: dict[str, Any] = {
            "station": data.get("meta", {}).get("station"),
            "generated": data.get("meta", {}).get("generated"),
            "dewpoint": _current(data, "dewpoint"),
            "rain_today": _current(data, "rain"),
        }
        radar = data.get(ATTR_RADAR)
        if isinstance(radar, dict):
            attrs["radar"] = {
                "raining_now": radar.get("raining_now"),
                "eta_min": radar.get("eta_min"),
                "total_mm": radar.get("total_mm"),
                "intensity": radar.get("intensity"),
            }
        return attrs


def _current(data: dict[str, Any] | None, key: str) -> Any:
    """Return a value from the current payload."""
    if not data:
        return None
    return (data.get("current") or {}).get(key)
