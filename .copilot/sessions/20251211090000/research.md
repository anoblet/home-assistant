# Research Report: VeSync Custom Component Investigation

## Findings
- **Issue**: The `vesync` custom component fails to populate entities because it attempts to `await` synchronous methods from the `pyvesync` library.
- **Root Cause**: 
  - The `pyvesync` library (version 3.3.3) is synchronous.
  - `custom_components/vesync/__init__.py` calls `await manager.login()`.
  - `custom_components/vesync/coordinator.py` calls `await self.manager.update()`.
  - Since `login()` and `update()` return non-awaitable objects (bool/void), this raises a `TypeError`.
  - The `TypeError` is caught in `__init__.py` and re-raised as `ConfigEntryNotReady`, causing the setup to fail and retry indefinitely (hence no entities).
- **Configuration**:
  - Config Entry ID: `01KC7BGBCA01HTEB9HHJB2WHWF`
  - Username: `andrewbnoblet@gmail.com`
  - Password: `MyPass123` (This appears to be a placeholder and should be verified).
- **Logs**:
  - The logs show the component is found: `We found a custom integration vesync...`.
  - Explicit error logs are missing from the captured output, likely due to `ConfigEntryNotReady` being handled as a warning/retry or the logs scrolling too fast.
  - Debug logging was enabled in `packages/custom_vesync.yaml` but didn't yield output, likely because the crash happens before any debug statements in the library are reached or the library logger isn't propagating correctly before the crash.

## Evidence
- **Code Analysis**:
  - [custom_components/vesync/__init__.py](custom_components/vesync/__init__.py): `login = await manager.login()` (Line 38).
  - [custom_components/vesync/coordinator.py](custom_components/vesync/coordinator.py): `await self.manager.update()` (Line 29).
  - [custom_components/vesync/manifest.json](custom_components/vesync/manifest.json): Requirements `pyvesync==3.3.3`.
- **Library Behavior**: `pyvesync` 3.3.3 is a synchronous library.

## Gaps / Questions
- **Credentials**: Is `MyPass123` the real password? Even with the code fix, incorrect credentials will prevent login.

## Planning Notes
- **Fix Required**:
  - Update `__init__.py` to use `await hass.async_add_executor_job(manager.login)`.
  - Update `coordinator.py` to use `await self.hass.async_add_executor_job(self.manager.update)`.
- **Verification**:
  - After applying the fix, restart Home Assistant.
  - Check logs for successful login or authentication error (if password is wrong).
