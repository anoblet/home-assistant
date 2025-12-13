# Fix Plan: Add Support for LUH-A602S-WUS Humidifier

## Overview

The issue is that the `is_humidifier` check in `custom_components/vesync/common.py` only looks for the string "humidifier" in the device type. The model `LUH-A602S-WUS` does not contain this string, so it is filtered out. The plan is to update this check to explicitly include this model.

## Steps

1.  **Modify `custom_components/vesync/common.py`**
    - **Action**: Update the `is_humidifier` function.
    - **Change**: Add a check for `luh-a602s-wus` (case-insensitive).
    - **Code**:
      ```python
      def is_humidifier(device_type):
          """Return true if the device is a humidifier."""
          return "humidifier" in device_type.lower() or "luh-a602s-wus" in device_type.lower()
      ```
    - **Validation**: Verify the file content after modification.

2.  **Restart Home Assistant**
    - **Action**: Run `ha core restart`.
    - **Expected Outcome**: Home Assistant restarts and reloads the integration.

3.  **Verify Fix**
    - **Action**: Check logs for successful device addition.
    - **Command**: `ha core logs | grep "LUH-A602S-WUS"` (or similar).
    - **Expected Outcome**: The device should no longer be ignored, and ideally, we see it being set up or at least not filtered out.

## Risks / Dependencies

- **Risk**: If the device type string in `pyvesync` is slightly different (e.g., extra spaces), the check might still fail.
  - _Mitigation_: Use `in` operator which is already planned.
- **Risk**: `pyvesync` might not be exposing the device in `manager.devices.fans` if it doesn't think it's a fan/humidifier, but the logs showed it was found, just filtered by HA integration.

## Expectations for Implement / Review

- The `is_humidifier` function will be updated.
- After restart, the "Bedroom Humidifier" entity should appear in Home Assistant.
