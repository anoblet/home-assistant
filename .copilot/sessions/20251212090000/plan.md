# Plan: Implement `vesync` Custom Component

## Overview
This plan outlines the creation of a `vesync` custom component by forking the official Home Assistant integration. The goal is to extend functionality to include VeSync Aura Thermostats (`climate`), Cosori Air Fryers (`sensor`/`switch`), and RGB/HSV support for compatible bulbs (`light`), while preserving all existing features.

## Steps

### Phase 1: Scaffolding & Setup
1.  **Scaffold Component Structure**
    *   **Action:** Create directory `custom_components/vesync`.
    *   **Action:** Copy the following files from the official integration (or create based on current source) to the new directory:
        *   `__init__.py`
        *   `const.py`
        *   `config_flow.py`
        *   `manifest.json`
        *   `common.py` (if applicable)
        *   `binary_sensor.py`, `fan.py`, `humidifier.py`, `light.py`, `number.py`, `select.py`, `sensor.py`, `switch.py`, `diagnostics.py`.
    *   **Validation:** Directory structure exists and contains base files.

2.  **Update Manifest & Dependencies**
    *   **Action:** Update `custom_components/vesync/manifest.json`.
        *   Add `"version": "1.0.0"`.
        *   Ensure `"requirements"` specifies a version of `pyvesync` that supports the new devices (e.g., `pyvesync>=2.1.12`).
        *   Ensure `"iot_class"` and `"config_flow"` are set correctly.
    *   **Validation:** `manifest.json` is valid JSON and contains the correct library version.

3.  **Update Device Discovery Logic (`__init__.py`)**
    *   **Action:** Modify `__init__.py` (specifically the `async_setup_entry` or device loading logic).
    *   **Action:** Ensure the manager retrieves and stores lists for `thermostats` and `kitchen` (Air Fryers) from the `VeSync` object. The official integration likely ignores these lists.
    *   **Action:** Register `climate` as a supported platform in `PLATFORMS`.
    *   **Validation:** Logs confirm that thermostat and kitchen devices are being detected and passed to platforms.

### Phase 2: New Platform Implementation

4.  **Implement Climate Platform (`climate.py`)**
    *   **Action:** Create `custom_components/vesync/climate.py`.
    *   **Action:** Implement `VeSyncClimate` class inheriting from `ClimateEntity`.
    *   **Action:** Map `pyvesync` thermostat attributes (mode, current temp, target temp, fan mode) to Home Assistant properties.
    *   **Action:** Implement methods: `async_set_hvac_mode`, `async_set_temperature`, `async_set_fan_mode`.
    *   **Validation:** `climate` entity appears for Aura Thermostat with correct controls.

5.  **Implement Air Fryer Support (`sensor.py` & `switch.py`)**
    *   **Action:** Update `custom_components/vesync/sensor.py`.
        *   Add logic to iterate over `manager.kitchen` devices (Air Fryers).
        *   Create sensor entities for: `current_temperature`, `cook_time_remaining`, `kitchen_mode` (status).
    *   **Action:** Update `custom_components/vesync/switch.py` (or create `button.py` if preferred, but switch is standard for toggleable states).
        *   Create a switch entity for "Cooking Status" (On = Cooking, Off = Stopped/Paused) if the API supports stopping.
    *   **Validation:** Sensors report fryer status; switch stops cooking (if supported).

### Phase 3: Enhancement of Existing Platforms

6.  **Update Light Platform (`light.py`)**
    *   **Action:** Modify `custom_components/vesync/light.py`.
    *   **Action:** Define a new class `VeSyncColorLightHA` inheriting from `VeSyncBaseLight`.
    *   **Action:** Implement `color_mode` support (`ColorMode.HS` or `ColorMode.RGB`).
    *   **Action:** Implement `async_turn_on` to handle `hs_color` or `rgb_color` arguments and call `device.set_rgb` or `device.set_hsv`.
    *   **Action:** Update the setup function to instantiate `VeSyncColorLightHA` for bulbs with color features (check `device.features` or model type).
    *   **Validation:** RGB bulb entity shows color picker in UI and changes color successfully.

### Phase 4: Verification

7.  **Testing & Verification**
    *   **Action:** Restart Home Assistant.
    *   **Action:** Check `home-assistant.log` for errors related to `custom_components.vesync`.
    *   **Action:** Verify all entities (old and new) are available and responsive.
    *   **Action:** Test specific interactions:
        *   Change Thermostat mode/temp.
        *   Read Air Fryer temp.
        *   Change Bulb color.

## Risks / Dependencies
*   **Dependency:** `pyvesync` library version must be recent enough to support the new device types.
*   **Risk:** The official integration's `common.py` or base classes might need adjustment to accommodate new device types if they assume a specific structure.
*   **Risk:** API Rate limits if polling is too aggressive for the new sensors.

## Expectations for Implement / Review
*   A complete `custom_components/vesync` folder.
*   `manifest.json` pointing to the correct domain and library.
*   Functional `climate` entity for thermostats.
*   Functional `sensor` entities for air fryers.
*   Color control for supported bulbs.
*   No regression in existing fans, outlets, or humidifiers.
