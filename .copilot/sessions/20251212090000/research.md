# Research Report: pyvesync vs. Home Assistant vesync Integration

## Findings

### 1. Supported Devices & Features in `pyvesync`

The `pyvesync` library (v3.0+) supports a wide range of VeSync devices with a structured, asynchronous API.

- **Outlets:**
  - Etekcity Voltson Smart WiFi Outlets (Round 7A/10A/15A, Rectangle 15A, Outdoor).
  - Features: On/Off, Energy Monitoring (Power, Voltage, Energy), Night Light (some models).
- **Switches:**
  - Etekcity Smart WiFi Light Switch & Dimmer.
  - Features: On/Off, Dimming.
- **Fans & Air Purifiers:**
  - Levoit Air Purifiers (Core series, Vital series, Everest Air, LV-PUR131S).
  - Tower Fans.
  - Features: Fan Speed, Modes (Auto, Sleep, Turbo, Pet, Manual), Air Quality (PM2.5), Filter Life, Display Control, Child Lock, Night Light.
- **Humidifiers:**
  - Levoit Humidifiers (Dual 200S, Classic 300S, LV600S, OasisMist series).
  - Features: Mist Level, Humidity Target, Modes (Auto, Manual, Sleep), Night Light, Warm Mist (some models).
- **Bulbs:**
  - Etekcity/Valceno Bulbs (Dimmable, Tunable White, Multi-Color).
  - Features: Brightness, Color Temperature, **RGB/HSV Color** (ESL100MC, XYD0001).
- **Air Fryers:**
  - Cosori Air Fryers (3.7 & 5.8 Quart).
  - Features: Status (Cooking, Heating, Standby), Current Temp, Target Temp, Remaining Time, Preheat Status, End Cooking.
- **Thermostats:**
  - VeSync Aura Thermostat.
  - Features: Target Temp (Heat/Cool), Current Temp, Humidity, Modes (Heat, Cool, Auto, Off), Fan Modes, Eco Mode, Schedule/Hold.

### 2. Home Assistant `vesync` Integration Implementation

The official integration currently implements the following platforms:

- **`fan`**: Supports Fans and Air Purifiers (Speed, Presets, Oscillation).
- **`light`**: Supports Bulbs and Dimmable Switches.
  - _Limitation:_ Only supports `ColorMode.BRIGHTNESS` and `ColorMode.COLOR_TEMP`.
- **`switch`**: Supports Outlets and Wall Switches. Also exposes auxiliary controls (Display, Child Lock) as switches.
- **`sensor`**: Supports Air Quality, Filter Life, Energy Monitoring, Humidity, Temperature (humidifiers).
- **`humidifier`**: Supports Humidifiers (Target Humidity, Modes).
- **`number`**: Supports Mist Level.
- **`select`**: Supports Night Light Level.
- **`binary_sensor`**: Supports Water Tank status.

### 3. Gaps & Missing Features

| Device / Feature       | `pyvesync` Capability                          | Home Assistant Implementation                      | Gap Severity |
| :--------------------- | :--------------------------------------------- | :------------------------------------------------- | :----------- |
| **Thermostats**        | Full support (Modes, Setpoints, Fan, Eco)      | **Missing**                                        | High         |
| **Air Fryers**         | Status, Temp, Time, Stop Control               | **Missing**                                        | Medium       |
| **RGB Bulbs**          | RGB & HSV Color Control (`set_rgb`, `set_hsv`) | **Missing** (Only Dimming/Tunable White supported) | Medium       |
| **Air Fryer Sensors**  | Current Temp, Remaining Time, Cook Status      | **Missing**                                        | Medium       |
| **Thermostat Sensors** | Current Temp, Humidity                         | **Missing**                                        | High         |

## Evidence

- **Thermostats:** `pyvesync/devices/vesyncthermostat.py` defines `VeSyncAuraThermostat` with full climate control logic. HA integration has no `climate.py`.
- **Air Fryers:** `pyvesync/devices/vesynckitchen.py` defines `VeSyncAirFryer158` with cooking status and telemetry. HA integration has no logic to handle these devices.
- **RGB Bulbs:** `pyvesync/devices/vesyncbulb.py` defines `VeSyncBulbESL100MC` with `set_rgb` and `set_hsv`. HA's `light.py` only defines `VeSyncDimmableLightHA` and `VeSyncTunableWhiteLightHA`, ignoring color capabilities.

## Planning Notes

- **Thermostat Support:** Requires creating a `climate.py` platform in the `vesync` component, mapping `VeSyncAuraThermostat` attributes to HA `ClimateEntity`.
- **Air Fryer Support:** Could be implemented by adding `sensor.py` entries for temperature/time and potentially a `switch` or `button` to stop cooking. A read-only `sensor` for status is also needed.
- **RGB Support:** Update `light.py` to detect `VeSyncBulbESL100MC` (or check `dev.features` for color support) and implement a `VeSyncColorLightHA` class supporting `ColorMode.RGB` or `ColorMode.HS`.
