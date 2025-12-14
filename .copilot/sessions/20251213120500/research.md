# Research Report - Session 20251213120500

## Findings

### Current Implementation Status
The `custom_components/vesync` integration currently supports a wide range of VeSync devices with the following mapping:

*   **Fans (`fan.py`)**:
    *   **Features**: On/Off, Speed (Percentage), Preset Modes (`auto`, `sleep`, `turbo`, `pet`, `normal`, `advancedSleep`), Oscillation (Horizontal).
    *   **Attributes**: `active_time`, `display_status`, `child_lock`, `night_light`, `mode`.
    *   **Entities**: `child_lock` (Switch), `display` (Switch), `night_light` (Select/Switch depending on device).
*   **Humidifiers (`humidifier.py`)**:
    *   **Features**: On/Off, Mode (`auto`, `manual`, `sleep`, `humidity`), Target Humidity.
    *   **Entities**: `mist_level` (Number), `warm_mist_level` (Number), `night_light_level` (Select), `water_lacks` (Binary Sensor), `water_tank_lifted` (Binary Sensor).
*   **Sensors (`sensor.py`)**:
    *   Air Quality, PM2.5, Filter Life, Humidity, Temperature, Energy/Power (Outlets), Air Fryer status.

### HA Entity Feature Coverage
*   **FanEntity**:
    *   `SET_SPEED`: Implemented.
    *   `PRESET_MODE`: Implemented.
    *   `OSCILLATE`: Implemented (Horizontal only).
    *   `DIRECTION`: Not implemented (Hardware limitation).
*   **HumidifierEntity**:
    *   `MODES`: Implemented.
    *   `SET_HUMIDITY`: Implemented.
    *   `TOGGLE`: Implemented.

### `pyvesync` Capabilities vs Implementation
`pyvesync` exposes several features that are currently **not** utilized in the integration:

1.  **Timer**: Both Fans and Humidifiers have `set_timer`, `get_timer`, and `clear_timer`. This allows setting an off-timer (e.g., turn off in X minutes).
2.  **Drying Mode**: Some humidifiers (e.g., VeSyncHumid200300S) support `drying_mode` (`turn_on_drying_mode`, `turn_off_drying_mode`).
3.  **Vertical Oscillation**: Some fans support `vertical_oscillation` separate from horizontal. The current `fan.py` only toggles "oscillation" which usually maps to horizontal.
4.  **Mute**: Fans support `mute` (`toggle_mute`).
5.  **Auto Stop**: Humidifiers support `automatic_stop` (`toggle_automatic_stop`).

### Discrepancies
*   **Humidifier Target Humidity**: `humidifier.py` attempts to read `device.state.target_humidity` and falls back to `device.state.auto_humidity`. `pyvesync` documentation only explicitly lists `target_humidity` as a property. The fallback might be unnecessary or referring to a non-existent attribute in newer `pyvesync` versions.

## Evidence

*   **Code**:
    *   `custom_components/vesync/fan.py`: Implements `FanEntity`.
    *   `custom_components/vesync/humidifier.py`: Implements `HumidifierEntity`.
    *   `custom_components/vesync/number.py`: Implements `mist_level`, `warm_mist_level`.
    *   `custom_components/vesync/switch.py`: Implements `child_lock`, `display`.
*   **Documentation (`pyvesync`)**:
    *   **Humidifiers**: Lists `timer`, `drying_mode_status`, `warm_mist_level`, `nightlight_brightness`.
    *   **Fans**: Lists `timer`, `vertical_oscillation_status`, `mute_status`.

## Gaps / Questions

1.  **Timer Support**: Missing. Could be implemented as a `NumberEntity` (minutes) or `Button` (to clear).
2.  **Drying Mode**: Missing. Should be a `SwitchEntity` or `SelectEntity` (if it has levels, though docs suggest on/off).
3.  **Vertical Oscillation**: Missing. `FanEntity` only supports one `oscillate` flag. Vertical oscillation could be a separate `SwitchEntity`.
4.  **Mute**: Missing. Should be a `SwitchEntity`.
5.  **Auto Stop**: Missing. Should be a `SwitchEntity`.

## Planning Notes

*   **Priority**:
    *   **Low/Medium**: Adding Timer, Mute, Drying Mode, Vertical Oscillation. These are "nice to have" features that complete the integration.
*   **Implementation Suggestions**:
    *   **Timer**: Add `NumberEntity` for "Timer Duration" (0 = off/clear).
    *   **Vertical Oscillation**: Add `SwitchEntity` named "Vertical Oscillation".
    *   **Mute**: Add `SwitchEntity` named "Mute".
    *   **Drying Mode**: Add `SwitchEntity` named "Drying Mode".
    *   **Auto Stop**: Add `SwitchEntity` named "Auto Stop".
*   **Refactoring**:
    *   Consider removing `active_time` attribute from Fan if it's not useful, or move to a Sensor.
