"""Shared entity helpers for Kraichtal Wetter."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, NAME
from .coordinator import KraichtalWetterCoordinator


class KraichtalWetterEntity(CoordinatorEntity[KraichtalWetterCoordinator]):
    """Base entity for Kraichtal Wetter."""

    _attr_has_entity_name = True

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the shared weather station device."""
        station = (self.coordinator.data or {}).get("meta", {}).get("station", "Oberöwisheim")
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            name=NAME,
            manufacturer=MANUFACTURER,
            model=f"Wetterstation {station}",
            configuration_url="https://kraichtal-wetter.de/",
        )
