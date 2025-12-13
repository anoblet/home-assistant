# Documentation: VeSync Humidifier Enhancements

## Overview

This update enhances the `vesync` custom component to provide better integration for VeSync humidifiers, specifically adding support for warm mist control and improved status reporting.

## Changes

### Humidifier Entity (`humidifier.py`)

- **Device Class**: The humidifier entity now correctly reports its device class as `humidifier`.
- **Action Status**: The entity now reports its current action (`humidifying`, `idle`, or `off`) based on the device's mode and target humidity settings.
  - **Humidifying**: When the device is on and actively misting (Manual mode, or Auto/Sleep mode with current humidity < target).
  - **Idle**: When the device is on but not misting (Auto/Sleep mode with current humidity >= target).
  - **Off**: When the device is turned off.

### Number Entity (`number.py`)

- **Warm Mist Level**: A new number entity has been added to control the warm mist level for supported humidifiers (e.g., LV600S).
  - **Range**: 0 (Off) to 3 (High).
  - **Availability**: This entity is automatically created only for devices that support the `set_warm_mist` feature.

## Configuration

No changes to `configuration.yaml` are required. The new entities will appear automatically for supported devices after a restart.

## Verification

- Check the humidifier entity in the dashboard; it should now show "Humidifying" or "Idle" in the state attributes or UI badge.
- Look for a new "Warm Mist Level" number entity associated with the humidifier device.
