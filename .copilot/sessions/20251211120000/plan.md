# Plan: Fix VeSync Component Issues

## Overview
The goal is to restore functionality to the VeSync custom component by verifying credentials, enabling diagnostic logging, and resolving deprecation warnings. The approach prioritizes gaining visibility into the failure mode via debug logs while simultaneously ensuring configuration best practices (secrets) are followed.

## Steps

1.  **Verify Credential Configuration**
    *   **Action**: Check `secrets.yaml` for existing VeSync credentials and compare them with the configuration in `packages/custom_vesync.yaml` or the Config Entry.
    *   **Expected Outcome**: Confirm if `MyPass123` is a placeholder and if valid credentials exist in secrets.
    *   **Validation**: Presence of `vesync_username` and `vesync_password` in `secrets.yaml`.

2.  **Enable Debug Logging**
    *   **Action**: Edit `packages/custom_vesync.yaml` to uncomment or add the `logger` configuration for `custom_components.vesync` and `pyvesync`.
    *   **Expected Outcome**: Debug level logs will be generated upon restart.
    *   **Validation**: Verify `logger:` section includes `custom_components.vesync: debug`.

3.  **Address Deprecation Warnings**
    *   **Action**: Search for `DhcpServiceInfo` usage in `custom_components/vesync/` and update the import path or usage to align with modern Home Assistant standards.
    *   **Expected Outcome**: Elimination of the deprecation warning in logs.
    *   **Validation**: `grep` search confirms updated code usage.

4.  **Restart Home Assistant**
    *   **Action**: Execute the restart script (`./bin/start.sh` or equivalent) to reload the configuration and component.
    *   **Expected Outcome**: Home Assistant restarts successfully.
    *   **Validation**: Process is running and new logs are generated.

5.  **Analyze Logs**
    *   **Action**: Inspect `home-assistant.log` for VeSync-specific debug messages, authentication errors, or device discovery info.
    *   **Expected Outcome**: Clear indication of whether the issue is authentication (401/403) or API/Connection related.
    *   **Validation**: Presence of `[custom_components.vesync]` or `[pyvesync]` log entries.

## Risks / Dependencies
*   **Risk**: If `MyPass123` is incorrect and no secrets exist, the user will need to provide valid credentials manually.
*   **Risk**: Restarting Home Assistant will temporarily disrupt all automation services.
*   **Dependency**: The `vesync` component relies on the `pyvesync` library; connectivity to VeSync cloud is required.

## Expectations for Implement / Review
*   After implementation, the `home-assistant.log` should contain verbose output from the VeSync component.
*   If authentication fails, the logs will explicitly state "Invalid credentials" or similar.
*   The deprecation warning regarding `DhcpServiceInfo` should no longer appear in the startup logs.
