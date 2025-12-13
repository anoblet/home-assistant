# Debug Plan: VeSync 0 Devices

## Overview

We will enable debug logging for the VeSync integration and its underlying library (`pyvesync`) to capture the raw API responses from the VeSync cloud. This will help us determine if the issue is due to an empty device list returned by the API (possibly due to region mismatch) or a parsing issue within Home Assistant.

## Steps

1.  **Enable Debug Logging**
    - **Target**: `packages/logger.yaml`
    - **Action**: Uncomment the `logs:` section and add debug entries for `custom_components.vesync` and `pyvesync`.
    - **Expected Configuration**:
      ```yaml
      logger:
        logger:
          default: warning
          logs:
            custom_components.vesync: debug
            pyvesync: debug
      ```

2.  **Restart Home Assistant**
    - **Action**: Execute a restart of the Home Assistant core.
    - **Command**: `ha core restart` (or via UI).
    - **Validation**: Wait for Home Assistant to come back online.

3.  **Analyze Logs**
    - **Action**: Check `home-assistant.log` for "vesync" entries.
    - **Command**: `grep -i "vesync" home-assistant.log | tail -n 50`
    - **Goal**: Look for lines containing `[pyvesync] call_api` or JSON responses showing the device list.

4.  **Determine Region Fix**
    - **Decision**:
      - If logs show `[]` (empty list) for devices but login is successful, we likely need to force a different region (e.g., 'EU' instead of default 'US').
      - If logs show devices but they aren't added to HA, it's a parsing/integration issue.

## Risks / Dependencies

- **Restart Required**: Home Assistant will be unavailable for a few minutes.
- **Log Noise**: Debug logging can generate significant output; remember to disable it after debugging.

## Expectations for Implement / Review

- We expect to see a log entry similar to `[pyvesync] json_response: {"result": ...}`.
- This response will definitively confirm what the VeSync server is telling us.
