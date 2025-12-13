# Research Report: VeSync Custom Component

## 1. Overview
This report analyzes the official Home Assistant `vesync` integration and the `pyvesync` library to identify requirements for a custom component that extends functionality, specifically adding support for Air Fryers and Thermostats.

## 2. Official Home Assistant Integration
- **Path:** `homeassistant/components/vesync`
- **Platforms:** `binary_sensor`, `fan`, `humidifier`, `light`, `number`, `select`, `sensor`, `switch`, `update`.
- **Key Files:**
    - `__init__.py`: Setup logic, `VeSync` manager initialization, platform forwarding.
    - `common.py`: Helper functions (`is_fan`, `is_humidifier`, etc.).
    - `coordinator.py`: `VeSyncDataCoordinator` for polling updates.
    - `fan.py`: Handles Air Purifiers and Fans.
    - `humidifier.py`: Handles Humidifiers.
- **Limitations:**
    - No `climate` platform for Thermostats.
    - No support for Kitchen appliances (Air Fryers).

## 3. pyvesync Library
- **Version:** `3.3.3` (Matches HA).
- **Repository:** `webdjoe/pyvesync`
- **Supported Devices:**
    - **Outlets/Switches:** Fully supported in HA.
    - **Fans/Purifiers:** Fully supported in HA.
    - **Humidifiers:** Fully supported in HA.
    - **Bulbs:** Fully supported in HA.
    - **Air Fryers:** Supported in library (`VeSyncAirFryer158`), missing in HA.
    - **Thermostats:** Supported in library (`VeSyncAuraThermostat`), missing in HA.

## 4. Gap Analysis & Requirements

### 4.1. Air Fryers
- **Library Class:** `VeSyncAirFryer158` (in `src/pyvesync/devices/vesynckitchen.py`).
- **Features:**
    - **Sensors:** Current Temperature, Cook Set Temp, Cook Set Time, Remaining Time, Cook Status (Cooking, Heating, Standby), Recipe ID/Name.
    - **Binary Sensors:** Is Heating, Is Cooking, Is Preheating.
    - **Controls:** `end()` method to stop cooking. No start/toggle support.
- **HA Implementation Plan:**
    - **Sensors:** Add to `sensor.py` (Temperature, Time, Status).
    - **Binary Sensors:** Add to `binary_sensor.py` (Running status).
    - **Button:** Add `button.py` to call `end()` (Stop Cooking).

### 4.2. Thermostats
- **Library Class:** `VeSyncAuraThermostat` (in `src/pyvesync/devices/vesyncthermostat.py`).
- **Features:**
    - **Modes:** Heat, Cool, Auto, Off.
    - **Attributes:** Current Temp, Target Temp (Heat/Cool), Humidity, Fan Mode.
- **HA Implementation Plan:**
    - **Climate:** Create `climate.py` to handle `VeSyncAuraThermostat`.
    - **Mapping:** Map `ThermostatWorkModes` to HA `HVACMode`.

### 4.3. Architecture Updates
- **`common.py`:** Add `is_air_fryer(device)` and `is_thermostat(device)` helpers.
- **`__init__.py`:** Add `Platform.CLIMATE` and `Platform.BUTTON` to `PLATFORMS`.
- **`const.py`:** Add constants for Air Fryer and Thermostat specific attributes.

## 5. Proposed File Structure for Custom Component
The custom component should mirror the official one but include the new files and modifications.

```text
custom_components/vesync/
├── __init__.py          # Updated to include new platforms
├── binary_sensor.py     # Updated for Air Fryer
├── button.py            # NEW: For Air Fryer "Stop"
├── climate.py           # NEW: For Thermostat
├── common.py            # Updated helpers
├── config_flow.py       # Same as official
├── const.py             # Updated constants
├── coordinator.py       # Same as official
├── diagnostics.py       # Same as official
├── entity.py            # Same as official
├── fan.py               # Same as official
├── humidifier.py        # Same as official
├── light.py             # Same as official
├── manifest.json        # Updated version/requirements
├── number.py            # Same as official
├── select.py            # Same as official
├── sensor.py            # Updated for Air Fryer
├── services.yaml        # Same as official
├── strings.json         # Updated strings
├── switch.py            # Same as official
└── update.py            # Same as official
```

## 6. Implementation Details

### Air Fryer Mapping
| pyvesync Attribute | HA Platform | Entity Description |
|--------------------|-------------|--------------------|
| `current_temp`     | `sensor`    | Temperature        |
| `cook_status`      | `sensor`    | Status (enum)      |
| `remaining_time`   | `sensor`    | Duration (min)     |
| `is_cooking`       | `binary_sensor` | Running        |
| `end()`            | `button`    | Stop Cooking       |

### Thermostat Mapping
| pyvesync Attribute | HA Platform | Entity Description |
|--------------------|-------------|--------------------|
| `work_mode`        | `climate`   | HVAC Mode          |
| `current_temp`     | `climate`   | Current Temp       |
| `heat_to_temp`     | `climate`   | Target Temp Low    |
| `cool_to_temp`     | `climate`   | Target Temp High   |
| `fan_mode`         | `climate`   | Fan Mode           |
