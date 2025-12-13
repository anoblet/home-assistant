# Research Report: VeSync Fan & Humidifier Implementation Analysis

## Findings

### 1. Previous Session Summary

- **Library:** `pyvesync` (v3.3.3) supports a wide range of devices including Outlets, Switches, Fans, Air Purifiers, Humidifiers, Bulbs, Air Fryers, and Thermostats.
- **Integration Status:**
  - **Implemented:** Fans/Purifiers (`fan`), Humidifiers (`humidifier`), Outlets/Switches (`switch`), Sensors (`sensor`), Binary Sensors (`binary_sensor`), Numbers (`number`), Selects (`select`).
  - **Missing:** Thermostats (`climate`), Air Fryers (partial), RGB Bulbs (color control).
- **Identified Gaps:** Thermostat support, Air Fryer control/sensors, RGB color control.

### 2. Current `custom_components/vesync` Implementation

#### Fan (Air Purifier) - `fan.py`

- **Entity:** `VeSyncFanHA` (inherits `FanEntity`).
- **Features:**
  - **Speed:** Implemented via `percentage` (1-100) and `speed_count`. Correctly maps device levels.
  - **Presets:** Implemented via `preset_mode`. Supports `auto`, `sleep`, `advancedSleep`, `turbo`, `pet`, `normal`.
  - **Oscillation:** Implemented via `oscillate` (if supported by device).
  - **Power:** `turn_on`, `turn_off`.
- **Auxiliary Entities:**
  - **Sensors:** Filter Life, Air Quality, PM2.5 (`sensor.py`).
  - **Switches:** Display, Child Lock (`switch.py`).
  - **Selects:** Night Light Level (`select.py`).
- **Compliance:** Follows modern `FanEntity` standards (uses `percentage` instead of deprecated `speed`).

#### Humidifier - `humidifier.py`

- **Entity:** `VeSyncHumidifierHA` (inherits `HumidifierEntity`).
- **Features:**
  - **Humidity:** `target_humidity`, `current_humidity`, `min_humidity`, `max_humidity`.
  - **Modes:** `mode` (Auto, Manual, Sleep). Maps `VS_TO_HA_MODE_MAP`.
  - **Power:** `turn_on`, `turn_off`.
- **Auxiliary Entities:**
  - **Numbers:** Mist Level (`number.py`).
  - **Selects:** Night Light Level (`select.py`).
  - **Sensors:** Humidity, Temperature (`sensor.py`).
  - **Binary Sensors:** Water Lacks, Water Tank Lifted (`binary_sensor.py`).
  - **Switches:** Display, Child Lock (`switch.py`).

### 3. Gaps & Missing Features (vs. HA Standards & Device Capabilities)

| Feature               | Component       | Status      | Recommendation                                                                                                                       |
| :-------------------- | :-------------- | :---------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| **Humidifier Action** | `humidifier.py` | **Missing** | Implement `action` property to report `humidifying`, `drying`, `idle`, or `off`.                                                     |
| **Device Class**      | `humidifier.py` | **Missing** | Set `_attr_device_class = HumidifierDeviceClass.HUMIDIFIER`.                                                                         |
| **Warm Mist**         | `number.py`     | **Missing** | Many Levoit humidifiers (e.g., LV600S) support Warm Mist (0-3). This should be a separate `number` entity if `pyvesync` supports it. |
| **UVC Light**         | `switch.py`     | **Missing** | Some models have UVC sterilization. Should be a `switch` if supported.                                                               |
| **Drying Mode**       | `humidifier.py` | **Missing** | Newer models might support drying. Check `pyvesync` for support.                                                                     |
| **Fan Direction**     | `fan.py`        | **N/A**     | Not typically applicable to Air Purifiers.                                                                                           |
| **Preset Modes**      | `fan.py`        | **Static**  | The list of presets is hardcoded (`VS_FAN_MODE_PRESET_LIST_HA`). If `pyvesync` adds new modes, they won't appear automatically.      |

### 4. `pyvesync` Library Research

- **Version:** 3.3.3 (confirmed in `manifest.json`).
- **Inferred Capabilities:**
  - `set_mist_level(value)`: Used for Cool Mist.
  - `set_humidity(value)`: Used for Target Humidity.
  - `set_mode(value)`: Used for Operation Mode.
  - `set_nightlight_brightness(value)`: Used for Night Light.
- **Unknowns:**
  - **Warm Mist:** No evidence of `set_warm_mist` usage in current component. Requires checking `pyvesync` source or documentation to confirm availability.
  - **UVC:** No evidence of usage.

## Evidence

- `custom_components/vesync/fan.py`: Implements `percentage` and `preset_mode`.
- `custom_components/vesync/humidifier.py`: Implements `HumidifierEntity` but lacks `action` and `device_class`.
- `custom_components/vesync/number.py`: Only implements `mist_level`.
- `custom_components/vesync/strings.json`: Confirms lack of "Warm Mist" or "UVC" translations.

## Planning Notes

- **Immediate Fixes:**
  1.  Add `action` property to `VeSyncHumidifierHA` in `humidifier.py`.
  2.  Add `device_class` to `VeSyncHumidifierHA` in `humidifier.py`.
- **Investigation Needed:**
  1.  Check if `pyvesync` supports Warm Mist (look for `warm_mist` or similar in library if possible, or try to inspect device object at runtime).
  2.  If supported, add `warm_mist_level` to `number.py`.
