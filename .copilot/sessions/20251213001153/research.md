## Findings
- **HA Fan model vs `custom_components/vesync`**
  - Implements core Fan model features used by HA: `TURN_ON`, `TURN_OFF`, `SET_SPEED` (percentage), `PRESET_MODE`; conditionally `OSCILLATE`.
  - Does **not** implement `DIRECTION` (no evidence of reverse-direction support in `pyvesync` fan docs).
  - Uses HA-recommended percentage conversion utilities (`ordered_list_item_to_percentage`, `percentage_to_ordered_list_item`).
  - Potential best-practice issue: post-command state updates mostly call `schedule_update_ha_state()` instead of `coordinator.async_request_refresh()`, which can leave state stale until the next poll.

- **HA Humidifier model vs `custom_components/vesync`**
  - Implements Humidifier core model: `is_on`, `available_modes`, `mode`, `current_humidity`, `min_humidity`/`max_humidity`, `turn_on`/`turn_off`, `set_mode`, `set_humidity`.
  - Likely **incorrect `target_humidity` mapping**: returns `device.state.auto_humidity` instead of the device’s real target humidity.
    - `pyvesync` docs describe `HumidifierState.auto_humidity` as “auto humidity level” and a separate `HumidifierState.target_humidity` as “target humidity level”.
  - Another best-practice issue: `async_set_humidity()` does not schedule a refresh, so HA UI may not reflect the updated target until the next coordinator poll.

- **`pyvesync` capability mismatches discovered in related entities** (not strictly HA Humidifier model, but impacts completeness of exposed device controls)
  - Warm mist control: integration’s number entity uses `set_warm_mist()` and checks `hasattr(device, "set_warm_mist")`, but `pyvesync` docs show `set_warm_level(warm_level: int)`.

- **Dispatcher / discovery signal mismatch**
  - All platforms subscribe to `VS_DISCOVERY.format(VS_DEVICES)` which resolves to `vesync_discovery_devices`.
  - The `update_devices` service sends `"vesync_new_devices"` instead, so newly discovered devices may not be forwarded to platform discovery callbacks.

- **Coordinator usage / best practice**
  - `VeSyncDataCoordinator` exists and polls `manager.update_all_devices()` every 60s.
  - `async_setup_entry` creates the coordinator but does not call `await coordinator.async_config_entry_first_refresh()`.
  - Several entities call `schedule_update_ha_state()` after commands; at least one entity (`select.py`) correctly calls `await self.coordinator.async_request_refresh()`.

- **Service description incomplete**
  - `custom_components/vesync/services.yaml` contains only the service key `update_devices:` with no schema/description.

## Evidence
- HA Fan entity model docs (supported features and property expectations): https://developers.home-assistant.io/docs/core/entity/fan/
- HA Humidifier entity model docs (supported features and property expectations): https://developers.home-assistant.io/docs/core/entity/humidifier/
- Integration Fan implementation: `custom_components/vesync/fan.py`
  - Supported features: `SET_SPEED | PRESET_MODE | TURN_OFF | TURN_ON`, plus `OSCILLATE` if `state.oscillation_status` exists.
  - Uses `ordered_list_item_to_percentage` / `percentage_to_ordered_list_item`.
- Integration Humidifier implementation: `custom_components/vesync/humidifier.py`
  - `target_humidity` returns `self.device.state.auto_humidity`.
- Integration warm mist number: `custom_components/vesync/number.py`
  - Uses `hasattr(device, "set_warm_mist")` and calls `device.set_warm_mist(int(value))`.
- Discovery constants: `custom_components/vesync/const.py` (`VS_DISCOVERY = "vesync_discovery_{}"`)
- Update service dispatcher send: `custom_components/vesync/__init__.py` sends `"vesync_new_devices"`.
- Coordinator implementation: `custom_components/vesync/coordinator.py`.
- Example of correct post-command refresh: `custom_components/vesync/select.py` uses `await self.coordinator.async_request_refresh()`.
- `pyvesync` docs:
  - Humidifiers (state + target humidity vs auto humidity): https://webdjoe.github.io/pyvesync/latest/devices/humidifiers/
  - Fans (oscillation capabilities richer than HA’s single OSCILLATE bool): https://webdjoe.github.io/pyvesync/latest/devices/fans/
  - Device capability mapping (modes/features by model): https://webdjoe.github.io/pyvesync/latest/development/device_map/

## Gaps / Questions
- Confirm in installed `pyvesync==3.3.3` (pinned in `custom_components/vesync/manifest.json`) whether the humidifier object exposes:
  - `device.state.target_humidity` vs `device.state.auto_target_humidity` vs `device.state.auto_humidity`, and which one is updated by `device.set_humidity()`.
- Confirm warm mist API in `pyvesync==3.3.3` for humidifiers:
  - Is the method `set_warm_level()` (docs) or does `set_warm_mist()` exist as an alias in this pinned version?
- Determine whether the coordinator ever starts periodic refresh without an explicit `async_config_entry_first_refresh()` call (best practice says it should be called).

## Planning Notes
- Confidence (high): `target_humidity` mapping is wrong for at least some models; it contradicts `pyvesync` docs and is central to HA’s humidifier model.
- Confidence (high): dispatcher signal mismatch prevents `update_devices` from triggering platform discovery.
- Confidence (medium): warm mist number entity likely broken or missing for devices that support warm mist (depends on `pyvesync==3.3.3` API surface).
- Best-practice opportunities: standardize post-command refresh to `coordinator.async_request_refresh()`; add coordinator first refresh; complete `services.yaml` metadata.
