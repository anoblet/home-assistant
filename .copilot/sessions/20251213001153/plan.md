# Plan

## Overview
Close feature and best-practice gaps in `custom_components/vesync` for Fan (air purifier) and Humidifier entities by:
- Correctly mapping humidifier target humidity.
- Fixing warm mist control API compatibility with the pinned `pyvesync` version.
- Ensuring device rediscovery signaling works.
- Standardizing post-command refresh via the coordinator.
- Adding missing setup/metadata to reduce stale-state issues and improve observability.

## Strategy
### Tree of Thoughts (3 options)
1. **Minimal bugfix-only**: Fix humidifier `target_humidity`, warm mist API call, and discovery signal mismatch. Leave coordinator usage unchanged.
2. **Bugfix + coordinator best-practice**: Do (1) plus add first refresh and switch all post-command updates to `coordinator.async_request_refresh()`.
3. **Capability-driven refactor**: Introduce a capability layer per device model (feature flags), then map HA features from capabilities; larger change, more code churn.

### Evaluation
- **Option 1**: Feasible fast; risk low; impact medium (fixes correctness but may keep stale states).
- **Option 2**: Feasible; risk medium (more touch points); impact high (correctness + state freshness + more reliable UX).
- **Option 3**: Feasible but high risk/time; impact high but over-scoped for this issue.

### Selection
Proceed with **Option 2**. It addresses the concrete correctness bugs found in research and reduces the “stale UI state” issues caused by inconsistent refresh behavior.

## Steps
1. **Inventory current entity features**
   - Action: Enumerate supported features/attributes in `fan.py` and `humidifier.py` and compare to HA entity docs.
   - Expected outcome: A short checklist of what’s implemented vs missing; confirm no additional HA-required props are absent.
   - Validation: Documented checklist in session notes; no code changes yet.

2. **Confirm `pyvesync==3.3.3` API surface for humidifiers and warm mist**
   - Action: Verify which attributes exist on humidifier state (`target_humidity`, `auto_humidity`, etc.) and which method exists for warm mist (`set_warm_level` vs `set_warm_mist`).
   - Expected outcome: Precise mapping for target humidity and a compatible warm mist setter.
   - Validation: Local inspection of installed library source or import-time introspection; record exact member names.
   - Notes: This step gates the implementation details in Steps 3 and 4.

3. **Fix humidifier `target_humidity` mapping**
   - Action: Update humidifier entity to expose the real target humidity attribute corresponding to HA `target_humidity`.
   - Expected outcome: HA UI shows and updates the configured target humidity correctly.
   - Validation:
     - Change target humidity in UI.
     - Observe immediate state update (post-command refresh).
     - Confirm logs show command succeeded.

4. **Ensure humidifier commands trigger an immediate refresh**
   - Action: After `set_humidity`, `set_mode`, `turn_on`, and `turn_off`, request coordinator refresh instead of only scheduling state updates.
   - Expected outcome: State in HA updates immediately after commands.
   - Validation: Run each command and confirm state changes without waiting for the polling interval.

5. **Fix warm mist number entity compatibility**
   - Action: Update warm mist control to use the correct method name(s) for the pinned `pyvesync` version.
   - Expected outcome: Warm mist level entity successfully calls into the device API without attribute errors.
   - Validation: Set the warm mist number from HA and confirm no exceptions in `ha core log`.
   - Notes: Prefer a compatibility shim (check for both names) to avoid breaking upgrades/downgrades.

6. **Fix dispatcher signal mismatch for rediscovery**
   - Action: Align the dispatcher signal used by the update service with the signal subscribed by platform setups.
   - Expected outcome: Calling the “update devices” service triggers platform discovery callbacks and adds new devices/entities.
   - Validation:
     - Call service.
     - Confirm discovery callback logs and new entities appear (or at minimum, no mismatch).

7. **Add/ensure coordinator first refresh during setup**
   - Action: Ensure config entry setup performs an initial refresh before platforms rely on coordinator data.
   - Expected outcome: Entities start with correct initial state and fewer “unknown”/stale values.
   - Validation: Restart HA; confirm entities load with state populated quickly and no startup exceptions.

8. **Standardize post-command refresh approach across Fan and Humidifier entities**
   - Action: Replace uses of `schedule_update_ha_state()` after successful device commands with `coordinator.async_request_refresh()` where appropriate.
   - Expected outcome: Consistent state behavior across entity types.
   - Validation: Execute common fan commands (on/off, preset, percentage, oscillate) and confirm immediate state changes.
   - Parallelization: Can be done in parallel with Steps 5–7 once Step 2 is complete.

9. **Improve logging configuration for troubleshooting**
   - Action: Add/confirm logger entries for the integration namespace and any underlying library namespace, and ensure meaningful debug output on updates/commands.
   - Expected outcome: CLI logs provide sufficient signal to diagnose failures.
   - Validation: Enable debug; restart; verify logs show coordinator refresh cycles and command handling.

10. **Complete service metadata**
   - Action: Fill in `services.yaml` descriptions and fields for the update service.
   - Expected outcome: Service UI shows a clear description; aligns with HA conventions.
   - Validation: HA service UI shows the service with description/fields; no schema warnings.

11. **Run end-to-end verification loop**
   - Action: Restart HA and validate logs and behavior.
   - Expected outcome: No errors; fixed features behave correctly.
   - Validation commands:
     - `ha core restart`
     - `ha core log`

## Risks / Dependencies
- **Pinned library differences**: `pyvesync==3.3.3` may differ from online docs; mitigate by confirming API in Step 2 and coding defensively.
- **Coordinator refresh cost**: Refreshing after every command may add load or slow UI; mitigate by refreshing only after successful calls and relying on existing polling interval otherwise.
- **Discovery side effects**: Aligning dispatcher signals could cause duplicate discovery if other code paths also dispatch; mitigate by ensuring idempotent discovery callbacks and logging when they fire.
- **State attribute ambiguity**: Different humidifier models may expose different state fields; mitigate with `getattr` fallbacks and clear logging when a field is missing.

## Expectations for Implement / Review
- **Success criteria**
  - Humidifier `target_humidity` reflects the device’s target humidity (not auto humidity).
  - Warm mist entity works without attribute errors on the pinned library.
  - “Update devices” service triggers the same discovery signal that platforms subscribe to.
  - Fan/humidifier state updates immediately after commands (coordinator refresh).
  - HA restarts cleanly; CLI logs show no uncaught exceptions from `custom_components.vesync`.

- **Validation checklist**
  - Toggle fan on/off; set percentage; change preset; toggle oscillation (if supported).
  - Toggle humidifier on/off; set mode; set humidity; verify current vs target humidity properties.
  - Call update service; confirm discovery callback activity.
  - Confirm services metadata renders in UI.
