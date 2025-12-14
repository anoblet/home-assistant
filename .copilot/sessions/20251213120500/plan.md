# Implementation Plan - VeSync Feature Expansion

This plan outlines the steps to add Timer, Vertical Oscillation, Drying Mode, Mute, and Auto Stop features to the VeSync integration.

## Overview

We will extend the existing `number` and `switch` platforms in `custom_components/vesync` to support the new features. The `fan` and `humidifier` platforms iterate over the same device list, so adding entity descriptions to `number.py` and `switch.py` will automatically create these entities for compatible devices.

## Proposed Changes

### 1. Timer (Number Entity)
*   **File**: `custom_components/vesync/number.py`
*   **Entity Type**: `NumberEntity`
*   **Unit**: Minutes
*   **Range**: 0 - 1440 (24 hours)
*   **Logic**:
    *   Value 0: Clear timer.
    *   Value > 0: Set timer.
    *   Read: `device.timer.duration` (or equivalent from state).

### 2. Switches (Switch Entity)
*   **File**: `custom_components/vesync/switch.py`
*   **New Switches**:
    *   **Vertical Oscillation**: For fans supporting it.
    *   **Drying Mode**: For humidifiers supporting it.
    *   **Mute**: For fans/humidifiers supporting it.
    *   **Auto Stop**: For humidifiers supporting it.

## Steps

1.  **Modify `custom_components/vesync/number.py`**:
    *   Add helper functions `_get_timer_duration` and `_set_timer_duration`.
    *   Add `VeSyncNumberEntityDescription` for `timer`.
    *   Configure `exists_fn` to check for `set_timer` capability.

2.  **Modify `custom_components/vesync/switch.py`**:
    *   Add `VeSyncSwitchEntityDescription` for `vertical_oscillation`.
    *   Add `VeSyncSwitchEntityDescription` for `drying_mode`.
    *   Add `VeSyncSwitchEntityDescription` for `mute`.
    *   Add `VeSyncSwitchEntityDescription` for `auto_stop`.
    *   Configure `exists_fn` and `is_on` logic for each based on `pyvesync` device attributes.

3.  **Verification**:
    *   Run `ha core restart`.
    *   Check `home-assistant.log` for errors.
    *   Verify new entities appear in Home Assistant for relevant devices.

## Risks / Dependencies
*   **Attribute Availability**: We assume `pyvesync` exposes the necessary state attributes (e.g., `device.state.vertical_oscillation`). If these are missing from the `device.state` object, we may need to inspect `device.details` or other properties.
*   **Method Names**: We assume standard `pyvesync` method names (`turn_on_vertical_oscillation`, etc.). If these differ, the calls will fail.

## Expectations for Implement / Review
*   New entities should appear automatically for devices that support these features.
*   Controls should function as expected (setting timer updates device, toggling switches updates device).
