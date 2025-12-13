# Plan: Fix Air Purifier Detection

## Overview
The current implementation of `is_fan` in `custom_components/vesync/common.py` is too restrictive, checking against a hardcoded list of models. This prevents other Air Purifier models (like the Core series) from being detected. We will broaden this check to include any device type containing the string "purifier".

## Steps

1.  **Modify `custom_components/vesync/common.py`**
    *   **Action**: Update the `is_fan` function.
    *   **Change**: Change the return statement to check if "purifier" is in `device_type.lower()` OR if it matches the existing list.
    *   **Expected Outcome**: The function returns `True` for any device type string containing "purifier".

2.  **Restart Home Assistant**
    *   **Action**: Execute the restart script or command.
    *   **Expected Outcome**: Home Assistant reloads the `vesync` integration with the updated code.

3.  **Verify Fix**
    *   **Action**: Check `home-assistant.log` for successful discovery of the Air Purifier.
    *   **Expected Outcome**: Logs should show the Air Purifier being initialized (e.g., `DEBUG ... [pyvesync.devices.vesyncfan] ...`).

## Risks / Dependencies
*   **Risk**: If a device has "purifier" in its type but is not supported by the `VeSyncFan` class logic, it might cause errors during initialization.
*   **Mitigation**: The `pyvesync` library generally handles these devices, but we should monitor logs for exceptions.

## Expectations for Implement / Review
*   The `is_fan` function should look like:
    ```python
    def is_fan(device_type):
        """Return true if the device is a fan."""
        return "purifier" in device_type.lower() or device_type.lower() in ["lv-pur131s", "lv-pur131s-rx", "lv-h132s", "lv-h133s"]
    ```
*   After restart, the Air Purifier should be visible in the logs.
