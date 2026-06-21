"""Constants for the Kraichtal Wetter integration."""

from __future__ import annotations

DOMAIN = "kraichtal_wetter"
NAME = "Kraichtal Wetter"
MANUFACTURER = "kraichtal-wetter.de"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 30
MAX_SCAN_INTERVAL = 3600

CONF_SCAN_INTERVAL = "scan_interval"
CONF_INCLUDE_FORECAST = "include_forecast"
CONF_INCLUDE_RADAR = "include_radar"

DEFAULT_INCLUDE_FORECAST = True
DEFAULT_INCLUDE_RADAR = True

BASE_URL = "https://kraichtal-wetter.de"

ATTR_FORECAST = "forecast"
ATTR_RADAR = "radar"
ATTR_CURRENT_CONDITION = "current_condition"
