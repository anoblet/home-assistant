# Implementation Plan - VeSync Custom Component

## Overview
This plan outlines the creation of a custom component `vesync` to replace the built-in Home Assistant integration. The primary goal is to extend functionality to support **Air Fryers** and **Thermostats**, which are supported by the underlying `pyvesync` library but not exposed in Home Assistant.

## Prerequisites
-   **Library**: `pyvesync` (ensure version compatibility, likely >= 2.1.0, currently 3.3.3 in HA).
-   **Home Assistant**: Access to `custom_components` directory.

## File Structure
The component will be located at `/homeassistant/custom_components/vesync/`.

```text
custom_components/vesync/
├── __init__.py          # Setup, Platform loading (Updated)
├── binary_sensor.py     # Air Fryer Status (Updated)
├── button.py            # Air Fryer Control (New)
├── climate.py           # Thermostat Control (New)
├── common.py            # Device Type Helpers (Updated)
├── config_flow.py       # Authentication Flow
├── const.py             # Constants (Updated)
├── coordinator.py       # Data Update Coordinator
├── diagnostics.py       # Debugging
├── entity.py            # Base Entity Class
├── fan.py               # Fans/Purifiers
├── humidifier.py        # Humidifiers
├── light.py             # Bulbs/Switches
├── manifest.json        # Component Metadata
├── number.py            # Settings
├── select.py            # Settings
├── sensor.py            # Air Fryer Stats (Updated)
├── services.yaml        # Service Definitions
├── strings.json         # Translations
├── switch.py            # Outlets/Switches
└── update.py            # Firmware Updates
```

## Steps

### 1. Component Scaffolding
Create the basic metadata and constant definitions.

-   **`manifest.json`**:
    -   Domain: `vesync`
    -   Name: `VeSync (Custom)`
    -   Documentation: Link to repo.
    -   Dependencies: None.
    -   Requirements: `["pyvesync==3.3.3"]` (or latest stable).
    -   IoT Class: `cloud_polling`.
-   **`const.py`**:
    -   Define `DOMAIN = "vesync"`.
    -   Add `VS_AIRFRYER` and `VS_THERMOSTAT` to device type constants if needed for internal logic.
    -   Define default update intervals.

### 2. Configuration & Initialization
Set up the integration entry point and platform loading.

-   **`config_flow.py`**:
    -   Implement `VeSyncConfigFlow`.
    -   Handle username/password input.
    -   Authenticate using `pyvesync.VeSync`.
-   **`__init__.py`**:
    -   Initialize `VeSync` object.
    -   Login and update devices.
    -   Setup `VeSyncDataCoordinator`.
    -   **Crucial**: Add `Platform.CLIMATE` and `Platform.BUTTON` to the `PLATFORMS` list.
    -   Forward setup to all platforms.

### 3. Shared Logic & Helpers
Update helper functions to recognize the new device types.

-   **`common.py`**:
    -   Implement `async_get_config_id(config_entry)`.
    -   **Update**: Add `is_air_fryer(device_type)` helper.
    -   **Update**: Add `is_thermostat(device_type)` helper.
-   **`coordinator.py`**:
    -   Ensure `VeSyncDataCoordinator` fetches data for all device lists (`manager.fans`, `manager.outlets`, `manager.bulbs`, `manager.kitchen` (Air Fryers), `manager.thermostats` (if separated in library)).

### 4. Implement Thermostat Support (`climate.py`)
Create the `climate` platform for VeSync Thermostats.

-   **Class**: `VeSyncThermostat(VeSyncBaseEntity, ClimateEntity)`
-   **Attributes**:
    -   `hvac_modes`: Map `pyvesync` modes to `HVACMode.HEAT`, `HVACMode.COOL`, `HVACMode.AUTO`, `HVACMode.OFF`.
    -   `current_temperature`: From `device.details['current_temp']`.
    -   `target_temperature`: From `device.details['heat_to_temp']` or `cool_to_temp` depending on mode.
    -   `fan_modes`: If supported.
-   **Methods**:
    -   `async_set_hvac_mode`: Call `device.set_mode()`.
    -   `async_set_temperature`: Call `device.set_target_temp()`.

### 5. Implement Air Fryer Support
Air Fryers require multiple platforms to expose their state and control.

-   **`button.py`** (New):
    -   **Class**: `VeSyncAirFryerButton(VeSyncBaseEntity, ButtonEntity)`
    -   **Function**: "Stop Cooking".
    -   **Method**: `async_press` calls `device.end()`.
-   **`sensor.py`** (Update):
    -   **Class**: `VeSyncAirFryerSensor(VeSyncBaseEntity, SensorEntity)`
    -   **Entities**:
        -   Current Temperature (`device_class: temperature`)
        -   Cook Set Time
        -   Remaining Time (`device_class: duration`)
        -   Cook Status (Enum: Cooking, Heating, Standby)
        -   Recipe Name
-   **`binary_sensor.py`** (Update):
    -   **Class**: `VeSyncAirFryerBinarySensor`
    -   **Entities**:
        -   `is_cooking` (`device_class: running`)
        -   `is_heating` (`device_class: heat`)

### 6. Standard Platforms (Port/Update)
Ensure existing device support is maintained.

-   **`switch.py`**: Outlets and Wall Switches.
-   **`fan.py`**: Air Purifiers and Fans.
-   **`light.py`**: Smart Bulbs and Dimmer Switches.
-   **`humidifier.py`**: Humidifiers.
-   **`number.py`** / **`select.py`**: Configuration entities (Night light, fan speed presets, etc.).

### 7. Finalization
-   **`strings.json`**: Add translations for new config flow errors, device classes, or entity names.
-   **Testing**: Verify all entities appear and update correctly.

## Risks & Dependencies
-   **`pyvesync` API**: The internal structure of `manager.kitchen` or `manager.thermostats` in the library must be verified to ensure correct iteration during setup.
-   **Polling Rate**: Ensure adding more devices doesn't hit API rate limits.

## Expectations
-   A fully functional `custom_components/vesync` directory.
-   Air Fryers appear with sensors and a stop button.
-   Thermostats appear as Climate entities.
-   Existing devices continue to work as before.
