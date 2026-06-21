"""Sensor platform for Kraichtal Wetter."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .api import last_chart_value
from .const import ATTR_RADAR, DOMAIN
from .coordinator import KraichtalWetterCoordinator
from .entity import KraichtalWetterEntity


@dataclass(frozen=True, kw_only=True)
class KraichtalSensorDescription(SensorEntityDescription):
    """Description of a Kraichtal Wetter sensor."""

    value_fn: Callable[[dict[str, Any]], Any]


SENSORS: tuple[KraichtalSensorDescription, ...] = (
    KraichtalSensorDescription(
        key="temperature",
        translation_key="temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("temp"),
    ),
    KraichtalSensorDescription(
        key="humidity",
        translation_key="humidity",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("humidity"),
    ),
    KraichtalSensorDescription(
        key="dewpoint",
        translation_key="dewpoint",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("dewpoint"),
    ),
    KraichtalSensorDescription(
        key="feels_like",
        translation_key="feels_like",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("feelsLike"),
    ),
    KraichtalSensorDescription(
        key="pressure",
        translation_key="pressure",
        native_unit_of_measurement=UnitOfPressure.HPA,
        device_class=SensorDeviceClass.PRESSURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("pressure"),
    ),
    KraichtalSensorDescription(
        key="wind_speed",
        translation_key="wind_speed",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("wind"),
    ),
    KraichtalSensorDescription(
        key="wind_gust",
        translation_key="wind_gust",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: last_chart_value(((data.get("charts") or {}).get("wind") or {}).get("gust")),
    ),
    KraichtalSensorDescription(
        key="solar",
        translation_key="solar",
        native_unit_of_measurement="W/m²",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("solar"),
    ),
    KraichtalSensorDescription(
        key="rain_today",
        translation_key="rain_today",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("current") or {}).get("rain"),
    ),
    KraichtalSensorDescription(
        key="rain_24h",
        translation_key="rain_24h",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("totals") or {}).get("rain24h"),
    ),
    KraichtalSensorDescription(
        key="rain_month",
        translation_key="rain_month",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: (data.get("totals") or {}).get("rainMonth"),
    ),
    KraichtalSensorDescription(
        key="rain_year",
        translation_key="rain_year",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.TOTAL,
        value_fn=lambda data: (data.get("totals") or {}).get("rainYear"),
    ),
    KraichtalSensorDescription(
        key="temp_max_today",
        translation_key="temp_max_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("dayStats") or {}).get("tempMax"),
    ),
    KraichtalSensorDescription(
        key="temp_min_today",
        translation_key="temp_min_today",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("dayStats") or {}).get("tempMin"),
    ),
    KraichtalSensorDescription(
        key="wind_max_today",
        translation_key="wind_max_today",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("dayStats") or {}).get("windMax"),
    ),
    KraichtalSensorDescription(
        key="gust_max_today",
        translation_key="gust_max_today",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get("dayStats") or {}).get("gustMax"),
    ),
    KraichtalSensorDescription(
        key="radar_eta",
        translation_key="radar_eta",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("eta_min"),
    ),
    KraichtalSensorDescription(
        key="radar_duration",
        translation_key="radar_duration",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("duration_min"),
    ),
    KraichtalSensorDescription(
        key="radar_total",
        translation_key="radar_total",
        native_unit_of_measurement="mm",
        device_class=SensorDeviceClass.PRECIPITATION,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("total_mm"),
    ),
    KraichtalSensorDescription(
        key="radar_intensity",
        translation_key="radar_intensity",
        icon="mdi:weather-pouring",
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("intensity"),
    ),
    KraichtalSensorDescription(
        key="radar_source",
        translation_key="radar_source",
        icon="mdi:radar",
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("source"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kraichtal Wetter sensors."""
    coordinator: KraichtalWetterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(KraichtalSensorEntity(coordinator, description) for description in SENSORS)


class KraichtalSensorEntity(KraichtalWetterEntity, SensorEntity):
    """Representation of a Kraichtal Wetter sensor."""

    entity_description: KraichtalSensorDescription

    def __init__(
        self,
        coordinator: KraichtalWetterCoordinator,
        description: KraichtalSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def native_value(self) -> Any:
        """Return the entity state."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose the original timestamp when available."""
        generated = (self.coordinator.data or {}).get("meta", {}).get("generated")
        if generated is None:
            return None
        return {"generated": generated}
