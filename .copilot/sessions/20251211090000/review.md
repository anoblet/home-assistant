# Review: VeSync Device Discovery

**Status**: FAIL

**Checklist Results**:
- [x] Verify "Bedroom Humidifier" (LUH-A602S-WUS) in logs. (FOUND)
- [ ] Verify "Air Purifier" in logs. (NOT FOUND)
- [ ] Verify "Second Humidifier" in logs. (NOT FOUND)
- [ ] Confirm 3 devices total. (FAIL: Only 1 found)

**Issues & Fixes**:
- **Issue**: `pyvesync` is only discovering one device. The other two are missing from the logs entirely.
- **Fix**:
    1.  Verify if the missing devices are supported by the installed version of `pyvesync`.
    2.  Check if `custom_components/vesync` is filtering them out *before* logging (unlikely as we checked `coordinator.py`).
    3.  The `is_fan` check in `common.py` might be an issue *if* they were found, but they aren't even in the logs.
    4.  Investigate `pyvesync` discovery logic.

**Notes for Implement / Supervisor**:
- The "Bedroom Humidifier" is working correctly.
- The other devices are completely absent from the logs.
