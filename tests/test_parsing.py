"""Unit tests for Kraichtal Wetter parsing helpers."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import ast
import unittest


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "custom_components"
    / "kraichtal_wetter"
    / "parsing.py"
)

spec = spec_from_file_location("kraichtal_wetter_parsing", MODULE_PATH)
parsing = module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(parsing)


SAMPLE_HTML = """
<div class="ww-fc-box ww-fc-today">
  <span class="ww-fc-badge">21.06.</span>
  <div class="ww-fc-box-main">
    <h4 class="title">Heute</h4>
    <div class="ww-fc-icon-wrap">
      <canvas class="ww-fc-main-icon" data-wx="scttsra-drz"></canvas>
    </div>
    <span class="ww-fc-tmax">35,6°C</span>
    <span class="ww-fc-tmin" style="visibility:hidden;">0°C</span>
    <div class="ww-pop-val" style="color:#9b59b6">30 %</div>
    <div class="ww-rain-val">0,2 mm</div>
  </div>
  <script>window.wwD=window.wwD||{};wwD[1]={t:[1,2]};</script>
</div>
<div class="ww-fc-box">
  <span class="ww-fc-badge">22.06.</span>
  <div class="ww-fc-box-main">
    <h4 class="title">Montag</h4>
    <div class="ww-fc-icon-wrap">
      <canvas class="ww-fc-main-icon" data-wx="few"></canvas>
    </div>
    <span class="ww-fc-tmax">35,2°C</span>
    <span class="ww-fc-tmin">20,7°C</span>
    <div class="ww-pop-val" style="color:#9b59b6">0 %</div>
    <div class="ww-rain-val">&#8211;</div>
  </div>
  <script>window.wwD=window.wwD||{};wwD[2]={t:[1,2]};</script>
</div>
"""


class ParsingTests(unittest.TestCase):
    def test_parse_forecast_extracts_cards(self) -> None:
        forecast = parsing.parse_forecast(
            SAMPLE_HTML,
            {"generated": "2026-06-21T18:03:18+02:00"},
        )

        self.assertEqual(len(forecast), 2)
        self.assertEqual(forecast[0]["datetime"], "2026-06-21")
        self.assertEqual(forecast[0]["native_temperature"], 35.6)
        self.assertIsNone(forecast[0]["native_templow"])
        self.assertEqual(forecast[0]["condition"], "lightning-rainy")
        self.assertEqual(forecast[0]["precipitation_probability"], 30)
        self.assertEqual(forecast[0]["native_precipitation"], 0.2)

        self.assertEqual(forecast[1]["datetime"], "2026-06-22")
        self.assertEqual(forecast[1]["condition"], "partlycloudy")
        self.assertEqual(forecast[1]["native_templow"], 20.7)
        self.assertIsNone(forecast[1]["native_precipitation"])

    def test_build_daily_forecast_keeps_ha_shape(self) -> None:
        daily = parsing.build_daily_forecast(
            [
                {
                    "datetime": "2026-06-21",
                    "condition": "sunny",
                    "native_temperature": 30.0,
                    "native_templow": 18.0,
                    "native_precipitation": 0.0,
                    "precipitation_probability": 10,
                    "label": "Heute",
                }
            ]
        )

        self.assertEqual(
            daily,
            [
                {
                    "datetime": "2026-06-21",
                    "condition": "sunny",
                    "native_temperature": 30.0,
                    "native_templow": 18.0,
                    "native_precipitation": 0.0,
                    "precipitation_probability": 10,
                }
            ],
        )

    def test_condition_and_wind_mapping(self) -> None:
        self.assertEqual(parsing.map_condition("nskc"), "clear-night")
        self.assertEqual(parsing.map_condition("bkn"), "cloudy")
        self.assertEqual(parsing.wind_bearing_from_text("ONO"), 67.5)
        self.assertEqual(
            parsing.derive_current_condition(
                {
                    "radar": {"raining_now": True},
                    "forecast": [{"condition": "sunny"}],
                }
            ),
            "rainy",
        )

    def test_weather_entity_forecast_method_is_not_property(self) -> None:
        weather_path = (
            Path(__file__).resolve().parents[1]
            / "custom_components"
            / "kraichtal_wetter"
            / "weather.py"
        )
        module = ast.parse(weather_path.read_text(encoding="utf-8"))

        weather_class = next(
            node for node in module.body if isinstance(node, ast.ClassDef) and node.name == "KraichtalWeatherEntity"
        )
        forecast_method = next(
            node
            for node in weather_class.body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_forecast_daily"
        )

        decorator_names = [
            decorator.id for decorator in forecast_method.decorator_list if isinstance(decorator, ast.Name)
        ]
        self.assertNotIn("property", decorator_names)

        forecast_property = next(
            node
            for node in weather_class.body
            if isinstance(node, ast.FunctionDef) and node.name == "forecast_daily"
        )
        property_decorators = [
            decorator.id for decorator in forecast_property.decorator_list if isinstance(decorator, ast.Name)
        ]
        self.assertIn("property", property_decorators)


if __name__ == "__main__":
    unittest.main()
