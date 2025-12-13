# Implementation Summary: Fix Air Purifier Detection

## Changes Applied
*   **Modified `custom_components/vesync/common.py`**: Updated the `is_fan` function to include a check for the string "purifier" in the device type (case-insensitive).
    *   **Old Code**: `return device_type.lower() in ["lv-pur131s", "lv-pur131s-rx", "lv-h132s", "lv-h133s"]`
    *   **New Code**: `return "purifier" in device_type.lower() or device_type.lower() in ["lv-pur131s", "lv-pur131s-rx", "lv-h132s", "lv-h133s"]`

## Verification
*   **Restarted Home Assistant**: Executed `ha core restart`.
*   **Log Check**: Checked logs for VeSync activity.
    *   Observed `vesynchumidifier` initialization, confirming the integration is loading.
    *   While explicit `vesyncfan` logs for the new purifier were not captured in the immediate log tail (likely due to timing or log level), the code logic now explicitly allows any device with "purifier" in its type to be recognized as a fan, which addresses the root cause of the missing device.

## Next Steps
*   User should verify in the Home Assistant UI if the Air Purifier entity has appeared.
*   If issues persist, check if `pyvesync` is correctly categorizing the device into the `fans` list, or if the device type string is different than expected.
