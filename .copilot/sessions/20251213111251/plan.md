# Plan: VeSync entity naming + full capability exposure (pyvesync 3.3.3)

## Overview
- **Goal**: (1) eliminate/avoid any entities ending with `_none` (specifically `switch.living_room_humidifier_none`) by fixing entity description naming/translation keys and handling existing entity-registry entries, and (2) expose all *reasonable* fan/air-purifier + humidifier capabilities from `pyvesync==3.3.3` as Home Assistant entities following HA platform best practices.
- **Chosen strategy (from 3 options)**: implement a targeted naming/translation fix + entity-registry migration for the `_none` switch, then perform a structured capability audit and add missing entities (sensor/switch/number/select/button) gated by explicit capability checks.
  - Alternatives considered: (a) minimal naming fix + manual registry cleanup only, (b) expose gaps via a single “attributes” sensor (lower UX quality), (c) services-only approach (doesn’t meet the “entities” requirement).

### Files likely to change (checklist)
- [ ] custom_components/vesync/switch.py
- [ ] custom_components/vesync/strings.json
- [ ] custom_components/vesync/__init__.py
- [ ] custom_components/vesync/sensor.py
- [ ] custom_components/vesync/binary_sensor.py
- [ ] custom_components/vesync/number.py (optional)
- [ ] custom_components/vesync/button.py (new)
- [ ] custom_components/vesync/icons.json (optional, if adding icons)

## Steps

1. [ ] **Confirm the `_none` root cause in the current code** → document which entity description is producing a `None` name
   - **Expected outcome**: evidence that `custom_components/vesync/switch.py` is creating a switch with `name=None` and no `translation_key`.
   - **Validation**:
     - Find `VeSyncSwitchEntityDescription(key="device_status", name=None, ...)`.
     - Confirm `custom_components/vesync/strings.json` has no `entity.switch.device_status` entry.
   - **Files**: custom_components/vesync/switch.py, custom_components/vesync/strings.json

2. [ ] **Fix switch naming/translation to prevent any new `_none` entities** → ensure every “aux” entity has a deterministic suffix name
   - **Expected outcome**: `device_status` switch has a real name via translations, so the generated entity_id becomes e.g. `switch.<device>_power` instead of `switch.<device>_none`.
   - **Implementation notes**:
     - In `custom_components/vesync/switch.py`, change the `device_status` description to use a real `translation_key` (recommend: `translation_key="power"`) and remove `name=None`.
     - Add the translation string under `entity.switch.power.name` in `custom_components/vesync/strings.json`.
     - Keep `description.key="device_status"` unchanged to avoid changing the entity unique_id.
   - **Validation**:
     - After restart (later steps), `ha entity list | grep _none` returns nothing.
     - The affected entity shows up as `switch.<slug>_power` (or similar), not `_none`.
   - **Files**: custom_components/vesync/switch.py, custom_components/vesync/strings.json

3. [ ] **Add an automatic migration/cleanup for existing `_none` entity_ids** → remove legacy `*_none` entity_ids without user intervention
   - **Why**: changing entity name/translation alone typically does **not** rename an existing entity_id stored in the entity registry.
   - **Expected outcome**: on upgrade/restart, HA renames or replaces `switch.*_none` (unique_id ending in `-device_status`) with the new, correct entity_id.
   - **Implementation notes**:
     - In `custom_components/vesync/__init__.py`, bump the config entry `minor_version` and extend `async_migrate_entry()`.
     - Migration logic:
       - Identify entity-registry entries for this config entry where:
         - domain is `switch`
         - unique_id ends with `-device_status`
         - entity_id ends with `_none`
       - Rename entity_id to a deterministic new one (recommend suffix `_power`).
       - If direct rename is not feasible in your HA version, remove the stale registry entry and allow the entity to be re-created with the same unique_id.
   - **Validation**:
     - `ha core log` includes a “Migrating …” line and the rename/remove operation.
     - Entity registry shows no `*_none` entries after restart.
   - **Files**: custom_components/vesync/__init__.py

4. [ ] **Audit pyvesync 3.3.3 purifier telemetry and add missing sensors** → expose reasonable air quality / environment metrics
   - **Expected outcome**: new sensors exist (only when supported by a given purifier model).
   - **Planned additions (gated by presence in `device.state`)**:
     - `pm1`, `pm10` (if present)
     - `voc` (if present)
     - `co2` (if present)
     - `aq_percent` (if present; typically %)
     - purifier ambient `temperature`, `humidity` (if present)
   - **Implementation notes**:
     - Add new `VeSyncSensorEntityDescription` entries in `custom_components/vesync/sensor.py`.
     - Prefer `translation_key` for each new sensor to ensure stable naming.
     - Assign appropriate `device_class`, unit, and `state_class=MEASUREMENT` where applicable.
   - **Validation**:
     - `ha entity list --domain sensor | grep vesync` shows the new sensors for supported devices.
     - `ha state get sensor.<...>` returns sane values (not `unknown`/exceptions) and updates on coordinator refresh.
   - **Files**: custom_components/vesync/sensor.py, custom_components/vesync/strings.json

5. [ ] **Expose purifier “filter door open” / similar states as binary sensors (if available)**
   - **Expected outcome**: a binary sensor is created when purifier state exposes `filter_open_state` (or equivalent).
   - **Implementation notes**:
     - Add a new `VeSyncBinarySensorEntityDescription` in `custom_components/vesync/binary_sensor.py` gated by `rgetattr(device, "state.filter_open_state") is not None`.
     - Choose the closest HA binary sensor device class (likely `PROBLEM` or `DOOR`) based on the actual semantics.
     - Add `translation_key` and strings.
   - **Validation**:
     - `ha entity list --domain binary_sensor | grep filter` shows the entity on supported devices.
   - **Files**: custom_components/vesync/binary_sensor.py, custom_components/vesync/strings.json

6. [ ] **Add purifier control switches for missing boolean capabilities** → expose `light_detection` and similar toggles
   - **Expected outcome**: if `pyvesync` supports `toggle_light_detection`, HA exposes a switch entity.
   - **Implementation notes**:
     - Add a `VeSyncSwitchEntityDescription` in `custom_components/vesync/switch.py`:
       - `exists_fn`: `hasattr(device, "toggle_light_detection")` or state attribute presence.
       - `is_on`: derived from a state field (confirm exact field name in coordinator data / device.state) or track last-set value if pyvesync doesn’t report it.
       - `on_fn/off_fn`: `device.toggle_light_detection(True/False)`.
     - Add translation strings.
   - **Validation**:
     - Toggling the switch triggers a coordinator refresh and no errors appear in `ha core log`.
   - **Files**: custom_components/vesync/switch.py, custom_components/vesync/strings.json

7. [ ] **Add a Button platform for one-shot purifier actions** → expose `reset_filter` as `button`
   - **Expected outcome**: a `button` entity appears for devices supporting filter reset.
   - **Implementation notes**:
     - Create a new platform file `custom_components/vesync/button.py`.
     - Add `Platform.BUTTON` to `PLATFORMS` in `custom_components/vesync/__init__.py`.
     - Implement a `ButtonEntityDescription` with `press_fn` calling `device.reset_filter()` (gated by `hasattr(device, "reset_filter")`).
     - Add translation strings in `custom_components/vesync/strings.json` under `entity.button`.
   - **Validation**:
     - `ha entity list --domain button | grep vesync` shows the entity.
     - Running `ha service call button.press --target entity_id=button.<...>` succeeds; logs show no exceptions.
   - **Files**: custom_components/vesync/button.py (new), custom_components/vesync/__init__.py, custom_components/vesync/strings.json

8. [ ] **Fill fan-base oscillation gaps from pyvesync 3.3.3** → expose horizontal oscillation and (optionally) oscillation angle configuration
   - **Expected outcome**: additional fan oscillation controls appear only on devices that support them.
   - **Planned additions**:
     - `switch.horizontal_oscillation` if `toggle_horizontal_oscillation` / `turn_on_horizontal_oscillation` exists.
     - Optional `number` entities for oscillation range/angle if pyvesync exposes setters and the valid range can be safely bounded.
   - **Implementation notes**:
     - Add a new switch description in `custom_components/vesync/switch.py` with `translation_key="horizontal_oscillation"`.
     - If adding numbers, extend `custom_components/vesync/number.py` with new descriptions gated by setter availability.
     - Add translations.
   - **Validation**:
     - Switch toggles without errors; if numbers added, setting values succeeds and refreshes state.
   - **Files**: custom_components/vesync/switch.py, custom_components/vesync/number.py (optional), custom_components/vesync/strings.json

9. [ ] **Fix fan preset-mode translation key mismatch** → ensure HA state translations actually match pyvesync mode values
   - **Expected outcome**: `advancedSleep` (camelCase) is translated correctly.
   - **Implementation notes**:
     - Update `custom_components/vesync/strings.json` under `entity.fan.vesync.state_attributes.preset_mode.state` to use `advancedSleep` instead of `advanced_sleep`.
   - **Validation**:
     - Fan preset mode displays the expected localized label.
   - **Files**: custom_components/vesync/strings.json

10. [ ] **Add/update logging to support per-entity verification** → make it easy to see which entities were created and why
   - **Expected outcome**: debug logs clearly show entity creation decisions for each platform and any capability gating.
   - **Implementation notes**:
     - Add concise debug statements in each platform setup loop only when needed (e.g., when skipping an entity because a capability is missing).
     - Avoid excessive logging each coordinator refresh.
   - **Validation**:
     - `ha core log` clearly indicates entity creation and does not spam repeatedly.
   - **Files**: custom_components/vesync/*.py (targeted)

11. [ ] **Verification runbook: verify each entity after restart with HA CLI and logs**
   - **Prereq**: enable integration debug logging (either via UI or config):
     - Set logger for the integration to debug (e.g., `custom_components.vesync: debug`).
   - **Restart + log tail**:
     - `ha core restart`
     - `ha core log -f` (keep running) and watch for `vesync` messages/exceptions.
   - **Registry checks (must be clean)**:
     - `ha entity list | grep _none` → should return nothing.
     - Optional deep check (if you have shell access): inspect `.storage/core.entity_registry` for `_none`.
   - **Per-entity checks (repeat for each entity on the device)**:
     - **State read**: `ha state get <entity_id>`
     - **Basic actuation** (where applicable):
       - switch: `ha service call switch.turn_on --target entity_id=<switch_id>` then `switch.turn_off`
       - fan: `ha service call fan.turn_on --target entity_id=<fan_id>` and `fan.set_percentage`
       - humidifier: `ha service call humidifier.set_humidity --target entity_id=<humidifier_id> --data humidity:<n>`
       - select: `ha service call select.select_option --target entity_id=<select_id> --data option:"<value>"`
       - number: `ha service call number.set_value --target entity_id=<number_id> --data value:<n>`
       - button: `ha service call button.press --target entity_id=<button_id>`
     - After each actuation: confirm `ha core log` shows no stack traces and `ha state get` reflects expected changes.
   - **Expected outcome**: every entity can be read; every controllable entity can be actuated; no `_none` entity ids exist.

## Risks / Dependencies
- **Entity registry inertia**: fixing translations won’t automatically rename existing entity_ids; migration logic (Step 3) is required to actually remove `*_none` from the registry without manual cleanup.
- **Capability ambiguity**: some pyvesync methods may not be supported consistently across all models; every new entity must be gated by `hasattr(...)` and/or state-field presence to prevent broken entities.
- **Units / device classes**: additional telemetry (VOC/CO2) must use correct HA device classes/units; validate against current HA constants.
- **API quota**: adding many new entities increases refresh surface area but should not increase API calls if all are fed from the same coordinator update.

### Additional capability to evaluate (purifiers)
- `set_auto_preference`: if pyvesync exposes a finite set of preference values, model this as `select`; if it’s numeric, model it as `number`. Gate entity creation on both setter presence and a readable state field.

## Expectations for Implement / Review
- **No `_none` entities**: `ha entity list | grep _none` returns empty after restart.
- **Coverage**: purifier + fan + humidifier devices expose (when supported) the documented pyvesync 3.3.3 telemetry and controls as separate HA entities, not hidden only in attributes.
- **HA alignment**:
  - sensors have appropriate `device_class`, unit, and `state_class`.
  - controls use the most suitable platform: `switch` for toggles, `select` for enumerations, `number` for ranges, `button` for one-shot actions.
  - naming uses `translation_key` + `strings.json` entries for stable, human-readable entity suffixes.
- **Verification**: each entity can be validated individually using `ha core log`, `ha entity list`, and `ha state get`, and every control can be actuated via `ha service call` without errors.

## Iteration 2: Correct state mappings + purifier auto preference select

### Overview
- **Goal**: fix incorrect entity state reporting for `mute`, `auto_stop`, and `drying_mode` switches (pyvesync 3.3.3 field names), and expose purifier auto preference as a `select` backed by pyvesync `state.auto_preference_type` and `device.auto_preferences`.
- **Optional**: align switch post-command behavior with the coordinator-driven platforms by requesting a coordinator refresh after toggles.

### Steps

1. **Fix switch state field mappings** → ensure UI reflects pyvesync 3.3.3 `device.state` fields
   - **Expected outcome**: `mute`, `auto_stop`, and `drying_mode` switches immediately show correct ON/OFF state after refresh and don’t get stuck OFF.
   - **Implementation notes** (pyvesync 3.3.3 confirmed fields):
     - `mute`: use `state.mute_status` (`"on"`/`"off"`), not `state.mute`.
     - `auto_stop`: use boolean `state.automatic_stop` (or `state.automatic_stop_config`), not `state.auto_stop`.
     - `drying_mode`: use `state.drying_mode_enabled` (or compare `state.drying_mode_status == "on"`), not `state.drying_mode`.
   - **Validation**:
     - `ha entity list --domain switch | grep -E '(mute|auto_stop|drying_mode)'` shows the entities.
     - Toggling each switch updates state correctly after a refresh.

2. **Add purifier auto preference as a select entity** → map `set_auto_preference` to HA `select`
   - **Expected outcome**: `select.<device>_auto_preference` appears for supported purifiers and can be changed via UI/service.
   - **Implementation notes**:
     - **Gating**: `is_purifier(device)` AND `hasattr(device, "set_auto_preference")` AND non-empty `getattr(device, "auto_preferences", None)`.
     - **Options**: use `list(device.auto_preferences)` so models can vary.
     - **Current option**: `device.state.auto_preference_type`; if `None` or not in `device.auto_preferences`, return `None`.
     - **Select action**: call `device.set_auto_preference(option)` (room_size left at pyvesync default).
     - Ensure the entity returns a consistent `unique_id` suffix (e.g., `-auto_preference`).
   - **Validation**:
     - `ha entity list --domain select | grep -i auto_preference` finds the entity on at least one purifier.
     - `ha state get select.<...>_auto_preference` returns one of the supported options (or `unknown`/`None` when device reports no value).
     - `ha service call select.select_option --target entity_id=select.<...>_auto_preference --data option:"default"` succeeds and state updates after refresh.

3. **(Optional) Refresh coordinator after switch toggles** → reduce UI lag and stale state
   - **Expected outcome**: switch state updates immediately after the toggle without waiting for the next poll.
   - **Implementation notes**:
     - After successful `on_fn/off_fn`, call `await self.coordinator.async_request_refresh()` (consistent with `select.py`, `number.py`, `button.py`).
     - Prefer refresh over `schedule_update_ha_state()` for coordinator-backed entities.
   - **Validation**: toggling a switch updates its state within one refresh cycle.

### Minimal file changes
- custom_components/vesync/switch.py
  - Update `is_on` lambdas for `mute`, `auto_stop`, `drying_mode` to use the correct `device.state.*` fields.
  - (Optional) replace `schedule_update_ha_state()` in `async_turn_on/off` with `await self.coordinator.async_request_refresh()`.
- custom_components/vesync/select.py
  - Add a new `VeSyncSelectEntityDescription` for purifier auto preference.
  - Ensure the entity can expose **dynamic options** sourced from `device.auto_preferences` (either via an `options_fn` in the description or an entity-level `options` override).
- custom_components/vesync/strings.json
  - Add `entity.select.auto_preference.name`.
  - Add `entity.select.auto_preference.state` mappings for known options (`default`, `efficient`, `quiet`).

### Verification commands
- Syntax / import sanity:
  - `python -m compileall custom_components/vesync`
- Runtime validation (after deploy into HA):
  - `ha core restart`
  - `ha core log -f`
  - `ha entity list --domain switch | grep -E '(mute|auto_stop|drying_mode)'`
  - `ha entity list --domain select | grep -i auto_preference`
  - `ha state get switch.<..._mute>`
  - `ha service call switch.turn_on --target entity_id=switch.<..._mute>`
  - `ha service call switch.turn_off --target entity_id=switch.<..._mute>`
  - `ha service call select.select_option --target entity_id=select.<..._auto_preference> --data option:"default"`
  - `ha state get select.<..._auto_preference>`
