# Kraichtal Wetter

Native Home Assistant Custom Integration fuer `https://kraichtal-wetter.de/`.

## HACS

Die Integration ist fuer HACS vorbereitet.

### Installation ueber HACS

1. Dieses Repository in HACS als benutzerdefiniertes Repository hinzufuegen.
2. Kategorie `Integration` waehlen.
3. `Kraichtal Wetter` in HACS installieren.
4. Home Assistant neu starten.
5. In Home Assistant `Einstellungen -> Geraete & Dienste -> Integration hinzufuegen`.
6. `Kraichtal Wetter` auswaehlen.

## Datenquellen

- `https://kraichtal-wetter.de/api/combined.php`
- `https://kraichtal-wetter.de/api/dwd_radar.php`
- `https://kraichtal-wetter.de/` fuer die Tagesvorhersage auf der Startseite

## Enthaltene Entities

- `weather.kraichtal_wetter`
- Sensoren fuer Temperatur, Luftfeuchtigkeit, Taupunkt, gefuehlte Temperatur, Luftdruck, Wind, Regen und Radar
- Binary Sensoren fuer Radar aktiv und Regen jetzt

## Installation

1. Diesen Ordner nach `config/custom_components/kraichtal_wetter` kopieren oder HACS verwenden.
2. Home Assistant neu starten.
3. In Home Assistant `Einstellungen -> Geraete & Dienste -> Integration hinzufuegen`.
4. `Kraichtal Wetter` auswaehlen.

## Hinweise

- Aktuelle Stationswerte kommen aus `api/combined.php`.
- Radarinformationen kommen aus `api/dwd_radar.php`.
- Die Tagesvorhersage wird direkt aus der Startseite geparst, weil `combined.php` derzeit keine nutzbaren Forecast-Felder liefert.
- Wenn sich das HTML der Startseite aendert, bleibt die Wetter-Entity nutzbar, aber die Forecast-Daten koennen ausfallen.
