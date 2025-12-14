# Plan: Verify and Improve VeSync Integration

## Overview
This plan aims to validate the runtime behavior of the `custom_components/vesync` integration. We will ensure that all expected entities (Fans, Humidifiers, and their auxiliary controls) are correctly created, available, and follow Home Assistant's naming conventions (`snake_case`). We will use the Home Assistant CLI for verification and code review to identify potential improvements.

## Steps

1.  **Restart Home Assistant**
    *   **Action**: Execute `ha core restart` in the terminal.
    *   **Expected Outcome**: Home Assistant restarts and reloads the `vesync` integration.
    *   **Validation**: The command returns successfully.

2.  **Check Logs for Errors**
    *   **Action**: Execute `ha core log` and search for "vesync" or "error".
    *   **Expected Outcome**: No critical errors related to `custom_components/vesync` or `pyvesync`.
    *   **Validation**: Log output is clean of relevant stack traces.

3.  **List and Verify Entities**
    *   **Action**: Execute `ha states list` and filter the output for entities related to VeSync devices (e.g., using `grep` for known device names or domains like `fan`, `humidifier`, `switch`, `number`, `select`).
    *   **Expected Outcome**: A list of entities including the main Fan/Humidifier and auxiliary entities (e.g., `switch.*_vertical_oscillation`, `number.*_mist_level`).
    *   **Validation**: All "missing" features identified in research (oscillation, mist level, etc.) appear as distinct entities.

4.  **Audit Naming Conventions**
    *   **Action**: Analyze the Entity IDs and Friendly Names from Step 3.
    *   **Expected Outcome**:
        *   Entity IDs use `snake_case` (e.g., `switch.bedroom_purifier_child_lock`).
        *   Auxiliary entities are clearly associated with their parent device in the ID.
    *   **Validation**: Identify any IDs that are ambiguous, generic, or malformed.

5.  **Review Naming Code**
    *   **Action**: Read `fan.py`, `humidifier.py`, `switch.py`, `number.py`, and `select.py` to examine how `_attr_name` and `entity_id` are generated.
    *   **Expected Outcome**: Confirm if the code explicitly handles naming or relies on default behavior which might need adjustment.
    *   **Validation**: Correlate code logic with the observed Entity IDs from Step 4.

6.  **Propose Improvements**
    *   **Action**: Create a list of recommended changes.
    *   **Expected Outcome**: A set of tasks to rename entities, move attributes, or fix labels if the audit in Steps 4 & 5 reveals issues.
    *   **Validation**: The proposal addresses any gaps found in the verification steps.

## Risks / Dependencies
*   **Risk**: `ha states list` might be verbose. Filtering is crucial.
*   **Risk**: If the device is offline, entities might be `unavailable` or not created if the integration requires initial connectivity.
*   **Dependency**: The `vesync` integration must be configured and loaded for entities to appear.

## Expectations for Implement / Review
*   The execution of this plan should result in a clear "Pass/Fail" for the integration's current state.
*   If "Fail" (or "Needs Improvement"), a specific list of code edits (e.g., "Change line X in `switch.py` to include device name") will be generated.
