# Implementation Plan - VeSync Humidifier Enhancements

This plan outlines the steps to enhance the VeSync integration by adding standard Humidifier features (`action`, `device_class`) and adding a new `number` entity for Warm Mist control.

## Overview
The goal is to bring the VeSync Humidifier entity up to Home Assistant standards and expose advanced features like Warm Mist levels. We will modify `humidifier.py` to add missing properties and `number.py` to add the new control entity.

## Steps

### 1. Analysis & Discovery
*   **Objective**: Understand the current codebase and verify library capabilities.
*   **Actions**:
    1.  Read `custom_components/vesync/humidifier.py` to identify available attributes on the `device` object (e.g., `details`, `config`).
    2.  Read `custom_components/vesync/number.py` to see how `VeSyncMistLevel` is implemented.
    3.  **Crucial**: Attempt to verify if the `pyvesync` library supports warm mist.
        *   *Note*: Since we cannot easily browse site-packages, we will assume the standard naming convention (`warm_mist_level` attribute and `set_warm_mist` method) but implement checks to ensure the device supports it before adding the entity.

### 2. Enhance Humidifier Entity (`humidifier.py`)
*   **Objective**: Add `action` and `device_class` properties.
*   **Actions**:
    1.  Import `HumidifierDeviceClass` and `HumidifierAction` from `homeassistant.components.humidifier.const`.
    2.  In `VeSyncHumidifierHA` class:
        *   Set `_attr_device_class = HumidifierDeviceClass.HUMIDIFIER`.
        *   Implement `@property action(self) -> HumidifierAction | None`:
            *   Return `HumidifierAction.OFF` if `self.is_on` is False.
            *   Return `HumidifierAction.DRYING` if mode is 'drying' (if supported).
            *   Return `HumidifierAction.HUMIDIFYING` if:
                *   Mode is 'manual' and mist level > 0.
                *   Mode is 'auto' and `current_humidity` < `target_humidity`.
            *   Return `HumidifierAction.IDLE` otherwise.
    3.  Verify `current_humidity` property exists and is correctly mapped.

### 3. Implement Warm Mist Number Entity (`number.py`)
*   **Objective**: Add control for Warm Mist levels.
*   **Actions**:
    1.  Define a new class `VeSyncWarmMistLevel` inheriting from `VeSyncNumberEntity`.
    2.  Implement properties:
        *   `native_max_value`: Check device capabilities (usually 3 or 4), default to 3.
        *   `native_min_value`: 0.
        *   `native_step`: 1.
        *   `native_value`: Return `self.device.details.get("warm_mist_level")`.
    3.  Implement `set_native_value`:
        *   Call `self.device.set_warm_mist(int(value))`.
    4.  Update `async_setup_entry`:
        *   Iterate through humidifiers.
        *   Check if the device has `warm_mist_level` in `details` or supports the feature.
        *   Add `VeSyncWarmMistLevel` entity if supported.

### 4. Verification
*   **Objective**: Ensure changes work and don't break existing functionality.
*   **Actions**:
    1.  Run `ha core check` to validate configuration (optional but good practice).
    2.  Run `ha core restart` to apply changes.
    3.  Run `ha core log` to check for errors, specifically `AttributeError` related to `warm_mist`.
    4.  Verify in UI:
        *   Humidifier entity shows correct icon/state (Humidifying/Idle).
        *   New "Warm Mist Level" number entity appears for supported devices.

## Risks / Dependencies
*   **Risk**: `pyvesync` library might use different method names for warm mist (e.g., `set_warm_level` instead of `set_warm_mist`).
    *   *Mitigation*: Wrap the method call in a `try/except` block or add debug logging if it fails.
*   **Risk**: `action` logic might be slightly off depending on how the device reports status in 'auto' mode.
    *   *Mitigation*: Rely on `target` vs `current` humidity comparison as a fallback.

## Expectations for Implement / Review
*   `humidifier.py` should have `action` and `device_class`.
*   `number.py` should have a new class for Warm Mist.
*   Logs should be clean of errors.
