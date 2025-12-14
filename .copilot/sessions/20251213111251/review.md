**Status**: PARTIAL — `_none` entity IDs are eliminated and migrations look safe, but a few new/updated entities appear to have incorrect state mappings vs `pyvesync==3.3.3`, and one notable purifier feature (`set_auto_preference`) is still not exposed.

**Checklist Results**
- No entities named `switch.living_room_humidifier_none`: PASS
  - Verified by searching `.storage/core.entity_registry` for `switch.living_room_humidifier_none` and `_none` (no matches).
- Every entity has a descriptive unique name: PASS (with a minor caveat)
  - All added entities use `translation_key` and/or `name` fallbacks; no `*_none` entity_ids appear in the entity registry.
  - Caveat: `.storage/core.restore_state` still contains stale `button.*_none` entries; these are not in the entity registry and appear to be historical restore-state remnants, but they can confuse audits.
- `custom_components/vesync` supports all reasonable fan/purifier + humidifier features from `pyvesync==3.3.3`: PARTIAL
  - Added/confirmed coverage: reset-filter button, light detection switch, filter-door binary sensor, extra purifier telemetry (PM1/PM10/VOC/CO₂/%), timer number, horizontal/vertical oscillation switches.
  - Gaps/concerns: missing `set_auto_preference` exposure; several switch `is_on` lambdas appear to reference non-existent state fields in `pyvesync==3.3.3`.
- Entity creation is capability-gated to avoid broken entities: PASS (with risks)
  - Most new entities are gated on `hasattr(...)` and/or state-field presence.
  - Risks noted below where gating is correct but state reporting likely incorrect.
- Migration logic is safe and compatible with HA entity registry: PASS
  - Config flow bumps `MINOR_VERSION = 6`, and `async_migrate_entry` handles `_none`, `_none_<n>` and collision cases with safe fallbacks (remove-then-recreate).

**Issues & Fixes**
- Severity: MAJOR — Incorrect switch state fields for `mute`, `auto_stop`, and `drying_mode`
  - Evidence (pyvesync 3.3.3 source):
    - Fan mute state is `state.mute_status` (not `state.mute`).
    - Humidifier auto-stop state is `state.automatic_stop_config` / property `state.automatic_stop` (not `state.auto_stop`).
    - Humidifier drying mode state is `state.drying_mode_status` / helper properties (not `state.drying_mode`).
  - Impact: entities may always display OFF/False (or otherwise wrong), which looks like “broken entities” even if service calls succeed.
  - Targeted fix: update the `is_on=` lambdas in `custom_components/vesync/switch.py`:
    - `mute`: compare `rgetattr(device, "state.mute_status") == "on"` (and/or handle enum values).
    - `auto_stop`: use `bool(rgetattr(device, "state.automatic_stop"))` or compare `state.automatic_stop_config`.
    - `drying_mode`: compare `rgetattr(device, "state.drying_mode_status") == "on"`.

- Severity: MAJOR — Missing purifier `set_auto_preference` feature mapping
  - Evidence: `pyvesync==3.3.3` exposes `set_auto_preference(preference: str, room_size: int=800)`.
  - Impact: integration is not “complete” for purifier controls; users can’t access a reasonable built-in purifier feature through HA entities.
  - Targeted fix: add a `select` entity (preferred) or a `number` + `select` pair:
    - `select.<device>_auto_preference` with options matching pyvesync supported preferences.
    - (Optional) `number.<device>_auto_room_size` if room size is useful and safe to bound.
    - Gate on `hasattr(device, "set_auto_preference")` and a readable state field (if present) to avoid “blind” entities.

- Severity: MINOR — Switch entities don’t request coordinator refresh after commands
  - Current pattern in `custom_components/vesync/switch.py` uses `schedule_update_ha_state()` after calling device methods.
  - Risk: UI may lag until next poll, and for toggles where pyvesync doesn’t eagerly mutate `device.state`, the state may remain stale.
  - Targeted fix: align with `number.py` / `select.py` / `button.py` by calling `await self.coordinator.async_request_refresh()` after successful on/off.

- Severity: MINOR — Capability gating may be overly restrictive in a few cases
  - Example: `light_detection` uses `supports_light_detection` (good), but for other toggles you sometimes require both a support flag and a specific method. In pyvesync 3.3.3 that’s usually fine, but it can reduce entity creation on edge models.
  - Targeted fix: prefer gating on `supports_*` OR the presence of the relevant method(s), not necessarily both.

**Notes for Implement / Supervisor**
- Naming/migration work is solid: the `_none` cleanup is robust and `MINOR_VERSION` alignment looks correct.
- Validation note: Supervisor `ha` CLI here doesn’t expose entity listing; verifying via `.storage/core.entity_registry` is the right approach. Consider adding a lightweight script/runbook command set that checks for `_none` in both entity registry and restore state so audits don’t get tripped up by historical entries.
- Recommended runtime spot-check after the state-field fixes:
  - Toggle `switch.*_mute`, `switch.*_auto_stop`, `switch.*_drying_mode` and confirm state updates immediately and persists after refresh.
  - Press `button.*_reset_filter` and ensure no stack traces in `ha core logs`.
