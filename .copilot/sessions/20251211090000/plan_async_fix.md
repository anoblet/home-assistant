# Plan: Fix Async/Await Usage in VeSync Integration

## Overview
The logs indicate a `RuntimeWarning: coroutine 'VeSync.login' was never awaited`. This suggests that an asynchronous method from the `pyvesync` library is being called without `await`, or is being treated as synchronous (e.g., wrapped in `async_add_executor_job` which returns the coroutine object but doesn't await it). This plan outlines the steps to identify and fix these missing awaits.

## Steps

1.  **Verify `__init__.py`**
    *   **Action**: Read `custom_components/vesync/__init__.py`.
    *   **Check**: Ensure `manager.login()` is called with `await`.
    *   **Expected Outcome**: Confirm it is `await manager.login()`.

2.  **Verify `coordinator.py`**
    *   **Action**: Read `custom_components/vesync/coordinator.py`.
    *   **Check**: Ensure `manager.update()` is called with `await`.
    *   **Expected Outcome**: Confirm it is `await manager.update()`.

3.  **Audit Platform Files for `async_add_executor_job`**
    *   **Action**: Scan `switch.py`, `fan.py`, `light.py`, `humidifier.py`, `number.py`, `select.py`, `climate.py`, `update.py` in `custom_components/vesync/`.
    *   **Check**: Look for `await self.hass.async_add_executor_job(self.device.method)`.
    *   **Reasoning**: If `pyvesync` has been updated to be async (implied by `login` being a coroutine), then wrapping these calls in `executor_job` is incorrect. It executes the function (returning a coroutine) but does not await the result.
    *   **Fix**: Replace with `await self.device.method()`.

4.  **Implement Fixes**
    *   **Action**: Apply the changes identified in Step 3.
    *   **Target**: Likely `switch.py`, `fan.py`, etc.

5.  **Verify Fix**
    *   **Action**: Restart Home Assistant.
    *   **Validation**: Check logs for `RuntimeWarning`. Verify device control works.

## Risks / Dependencies
*   **Risk**: If `pyvesync` has a mix of sync and async methods, we must be careful only to await the async ones.
    *   *Mitigation*: `login` and `update` are definitely async. We assume control methods like `turn_on`, `set_mode` are also async in the same version.
*   **Dependency**: Requires `pyvesync` library to be the version that supports async (which seems to be the case given the warning).

## Expectations for Implement / Review
*   The code in `__init__.py` might already be correct, so the focus will likely be on the platform files.
*   Success is defined by the absence of `RuntimeWarning` in the logs.
