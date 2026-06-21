"""Pure parsing helpers for Kraichtal Wetter."""

from __future__ import annotations

from datetime import UTC, datetime
import re
from typing import Any

_CARD_RE = re.compile(
    r'<div class="ww-fc-box[^>]*>(?P<card>.*?)'
    r'<script>window\.wwD=window\.wwD\|\|\{\};wwD\[(?P<idx>\d+)\]=\{(?P<data>[^;]+)\};</script>',
    re.DOTALL,
)

_FIELD_PATTERNS = {
    "date_label": re.compile(r'ww-fc-badge[^>]*>([^<]+)'),
    "label": re.compile(r'<h4 class="title">([^<]+)</h4>'),
    "temp_max": re.compile(r'ww-fc-tmax">([^<]+)'),
    "temp_min": re.compile(r'ww-fc-tmin[^>]*>([^<]+)'),
    "wx_code": re.compile(r'data-wx="([^"]+)"'),
    "precipitation_probability": re.compile(r'ww-pop-val[^>]*>([^<]+)'),
    "precipitation": re.compile(r'ww-rain-val">([^<]+)'),
}

_WIND_BEARINGS = {
    "N": 0.0,
    "NNO": 22.5,
    "NO": 45.0,
    "ONO": 67.5,
    "O": 90.0,
    "OSO": 112.5,
    "SO": 135.0,
    "SSO": 157.5,
    "S": 180.0,
    "SSW": 202.5,
    "SW": 225.0,
    "WSW": 247.5,
    "W": 270.0,
    "WNW": 292.5,
    "NW": 315.0,
    "NNW": 337.5,
}


def parse_forecast(html: str, meta: dict[str, Any]) -> list[dict[str, Any]]:
    """Parse daily forecast cards embedded on the homepage."""
    generated = _parse_generated(meta.get("generated"))
    forecasts: list[dict[str, Any]] = []
    last_date: datetime | None = None

    for match in _CARD_RE.finditer(html):
        card = match.group("card")
        date_label = _extract_field(card, "date_label")
        forecast_date = _date_from_label(date_label, generated, last_date)
        if forecast_date is None:
            continue

        wx_code = _extract_field(card, "wx_code") or ""
        forecast = {
            "datetime": forecast_date.date().isoformat(),
            "native_temperature": _parse_number(_extract_field(card, "temp_max")),
            "native_templow": _parse_number(_extract_field(card, "temp_min")),
            "native_precipitation": _parse_number(_extract_field(card, "precipitation")),
            "precipitation_probability": _parse_number(
                _extract_field(card, "precipitation_probability")
            ),
            "condition": map_condition(wx_code),
            "label": _extract_field(card, "label"),
            "wx_code": wx_code,
        }
        forecasts.append(forecast)
        last_date = forecast_date

    return forecasts


def build_daily_forecast(forecast: list[dict[str, Any]] | None) -> list[dict[str, Any]] | None:
    """Convert parsed forecast data into Home Assistant forecast dictionaries."""
    if not forecast:
        return None

    return [
        {
            "datetime": item["datetime"],
            "condition": item.get("condition"),
            "native_temperature": item.get("native_temperature"),
            "native_templow": item.get("native_templow"),
            "native_precipitation": item.get("native_precipitation"),
            "precipitation_probability": item.get("precipitation_probability"),
        }
        for item in forecast
    ]


def extract_field(card: str, field: str) -> str | None:
    """Extract a single field from a forecast card."""
    match = _FIELD_PATTERNS[field].search(card)
    if not match:
        return None

    value = match.group(1)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if value in {"", "0°C", "0 C", "–", "&#8211;"}:
        return None
    return value.replace("&#8211;", "-")


def derive_current_condition(data: dict[str, Any]) -> str | None:
    """Derive a Home Assistant weather condition."""
    radar = data.get("radar") or {}
    if radar.get("raining_now"):
        return "rainy"

    forecast = data.get("forecast") or []
    if forecast:
        first_condition = forecast[0].get("condition")
        if first_condition:
            return first_condition

    return None


def map_condition(wx_code: str | None) -> str | None:
    """Map Kraichtal homepage icon codes to Home Assistant conditions."""
    if not wx_code:
        return None

    code = wx_code.lower()
    if "tsra" in code:
        return "lightning-rainy"
    if "drizzle" in code or "drz" in code or "rain" in code:
        return "rainy"
    if code in {"skc", "sun"}:
        return "sunny"
    if code.startswith("n") and ("skc" in code or "few" in code):
        return "clear-night"
    if "few" in code or "sct" in code:
        return "partlycloudy"
    if "bkn" in code or "ovc" in code:
        return "cloudy"
    return None


def wind_bearing_from_text(direction: str | None) -> float | None:
    """Convert German wind direction abbreviations to degrees."""
    if not direction:
        return None
    return _WIND_BEARINGS.get(direction.upper())


def last_chart_value(values: list[Any] | None) -> float | None:
    """Return the last numeric chart value."""
    if not values:
        return None

    for value in reversed(values):
        if isinstance(value, (int, float)):
            return float(value)

    return None


def _extract_field(card: str, field: str) -> str | None:
    return extract_field(card, field)


def _parse_generated(value: Any) -> datetime:
    """Parse the generated timestamp from the JSON payload."""
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass

    return datetime.now(UTC)


def _date_from_label(
    label: str | None, reference: datetime, last_date: datetime | None
) -> datetime | None:
    """Build a date from a day label like 21.06."""
    if not label:
        return None

    clean = label.strip().rstrip(".")
    parts = clean.split(".")
    if len(parts) < 2:
        return None

    try:
        day = int(parts[0])
        month = int(parts[1])
    except ValueError:
        return None

    year = reference.year
    try:
        result = reference.replace(year=year, month=month, day=day)
    except ValueError:
        return None

    if last_date is not None and result.date() < last_date.date():
        try:
            result = result.replace(year=result.year + 1)
        except ValueError:
            return None

    return result


def _parse_number(value: str | None) -> float | int | None:
    """Extract the first numeric value from a string."""
    if value is None:
        return None

    normalized = (
        value.replace("°C", "")
        .replace("mm", "")
        .replace("%", "")
        .replace(",", ".")
        .strip()
    )
    match = re.search(r"-?\d+(?:\.\d+)?", normalized)
    if not match:
        return None

    number = float(match.group(0))
    if number.is_integer():
        return int(number)
    return number
