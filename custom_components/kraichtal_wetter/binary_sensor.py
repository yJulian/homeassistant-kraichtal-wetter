"""Binary sensors for Kraichtal Wetter radar state."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import ATTR_RADAR, DOMAIN
from .coordinator import KraichtalWetterCoordinator
from .entity import KraichtalWetterEntity


@dataclass(frozen=True, kw_only=True)
class KraichtalBinarySensorDescription(BinarySensorEntityDescription):
    """Description for Kraichtal Wetter binary sensors."""

    value_fn: Callable[[dict[str, Any]], bool | None]


BINARY_SENSORS: tuple[KraichtalBinarySensorDescription, ...] = (
    KraichtalBinarySensorDescription(
        key="radar_active",
        translation_key="radar_active",
        device_class=BinarySensorDeviceClass.MOISTURE,
        icon="mdi:radar",
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("active"),
    ),
    KraichtalBinarySensorDescription(
        key="raining_now",
        translation_key="raining_now",
        device_class=BinarySensorDeviceClass.MOISTURE,
        value_fn=lambda data: (data.get(ATTR_RADAR) or {}).get("raining_now"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Kraichtal Wetter binary sensors."""
    coordinator: KraichtalWetterCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        KraichtalBinarySensorEntity(coordinator, description)
        for description in BINARY_SENSORS
    )


class KraichtalBinarySensorEntity(KraichtalWetterEntity, BinarySensorEntity):
    """Representation of a Kraichtal Wetter binary sensor."""

    entity_description: KraichtalBinarySensorDescription

    def __init__(
        self,
        coordinator: KraichtalWetterCoordinator,
        description: KraichtalBinarySensorDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"

    @property
    def is_on(self) -> bool | None:
        """Return the binary sensor state."""
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Expose radar details for the binary sensors."""
        radar = (self.coordinator.data or {}).get(ATTR_RADAR)
        if not isinstance(radar, dict):
            return None
        return {
            "eta_min": radar.get("eta_min"),
            "duration_min": radar.get("duration_min"),
            "total_mm": radar.get("total_mm"),
            "intensity": radar.get("intensity"),
        }
