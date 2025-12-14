- **Findings**
  - VeSync integration pins `pyvesync==3.3.3`.
  - All VeSync entities inherit `_attr_has_entity_name = True` via the base class; aux entities rely on `entity_description` (name/translation/device_class) to produce a non-`None` entity name.
  - One switch entity description explicitly sets `name=None` and omits `translation_key` (`key="device_status"`), and there is no corresponding `entity.switch.device_status.name` entry in `strings.json`; this combination can yield an entity “name” of `None` and can plausibly produce an entity_id suffix `_none` when HA slugifies a `None` name.
  - Additional (lower-confidence) “name can be None” cases exist where entity descriptions omit `translation_key` (e.g., sensors relying on `device_class` naming). These should still have stable names in HA, but they’re the other places where `translation_key` is effectively `None`.
  - Air purifier coverage (HA integration): fan control (on/off, speed %, preset modes filtered from `device.modes`), sensors (`filter_life`, `air_quality_string`, `pm25`), switches (`display`, `child_lock`, `mute`), select (`night_light_level`), number (`timer`).
  - Air purifier coverage gaps vs pyvesync 3.3.3: additional telemetry (`pm1`, `pm10`, `voc`, `co2`, `aq_percent`, `temperature`, `humidity`, `fan_rotate_angle`, `filter_open_state`) and controls (`toggle_light_detection`, `set_auto_preference`, `reset_filter`) exist in pyvesync but are not mapped to HA entities here.
  - Humidifier coverage (HA integration): humidifier entity (modes + target humidity), sensors (humidity, temperature), binary sensors (low water / tank lifted), numbers (mist level, warm mist level when supported, timer), switches (display, auto stop, drying mode, child lock, mute), select (night light level).

- **Evidence**
  - pyvesync version pin: `/homeassistant/custom_components/vesync/manifest.json` (`requirements`: `pyvesync==3.3.3`).
  - Base naming behavior: `/homeassistant/custom_components/vesync/entity.py` sets `_attr_has_entity_name = True` for all entities.
  - Definite “name=None + no translation_key” entity description:
    - `/homeassistant/custom_components/vesync/switch.py`: `VeSyncSwitchEntityDescription(key="device_status", name=None, ...)` (no `translation_key=` parameter).
    - `/homeassistant/custom_components/vesync/strings.json`: under `entity.switch`, entries exist for `display`, `child_lock`, `drying_mode`, `mute`, `auto_stop`, etc., but not `device_status`.
  - Entity descriptions where `translation_key` is omitted (i.e., `translation_key` is `None` in the description) and naming depends on HA defaults:
    - `/homeassistant/custom_components/vesync/sensor.py`: `pm25`, `humidity`, `temperature` sensor descriptions omit `translation_key`.
  - pyvesync 3.3.3 purifier surface area (beyond what HA integration exposes):
    - `/tmp/pyvesync_src_333/pyvesync/base_devices/purifier_base.py`: async methods include `toggle_display`, `toggle_child_lock`, `set_nightlight_mode`, `set_fan_speed`, `set_auto_mode`, `set_sleep_mode`, `set_manual_mode`, `set_turbo_mode`, `set_pet_mode`, `toggle_light_detection`, `set_auto_preference`, `reset_filter`.
    - `/tmp/pyvesync_src_333/pyvesync/base_devices/purifier_base.py`: `PurifierState` documents/defines many telemetry fields (e.g., `pm1`, `pm10`, `voc`, `co2`, `aq_percent`, `temperature`, `humidity`, `light_detection_*`, `fan_rotate_angle`, `filter_open_state`).
  - pyvesync 3.3.3 fan surface area relevant to oscillation and modes:
    - `/tmp/pyvesync_src_333/pyvesync/base_devices/fan_base.py`: async methods include `set_advanced_sleep_mode`, `set_normal_mode`, `toggle_oscillation`, `toggle_vertical_oscillation`, `toggle_horizontal_oscillation`, and oscillation-range setters.
  - pyvesync 3.3.3 humidifier surface area:
    - `/tmp/pyvesync_src_333/pyvesync/base_devices/humidifier_base.py`: async methods include `set_mode`, `set_mist_level`, `set_humidity`, `toggle_display`, `toggle_automatic_stop`, `set_nightlight_brightness`, `toggle_nightlight`, `set_warm_level`, `toggle_drying_mode`.
    - `/tmp/pyvesync_src_333/pyvesync/devices/vesynchumidifier.py`: humidifier implementation provides `set_timer` / `clear_timer` and sets state fields such as humidity, mist levels, nightlight brightness, warm mist, and display status.

- **Gaps / Questions**
  - Confirm whether HA’s entity_id generation path is actually slugifying `None` → `"none"` for this integration in your environment (highly plausible given `name=None` + `has_entity_name=True`, but depends on HA core behavior/version).
  - For purifiers: decide whether to expose additional telemetry (`pm1`, `pm10`, `voc`, `co2`, `aq_percent`, `temperature`, `humidity`) and controls (`light_detection`, `auto_preference`, `reset_filter`) that exist in pyvesync 3.3.3.
  - For fans: integration exposes “vertical oscillation” but not “horizontal oscillation” or oscillation-range configuration, which exist in pyvesync 3.3.3.
  - Translation consistency: `const.py` uses `advancedSleep` but `strings.json` includes `advanced_sleep` under `fan.vesync.state_attributes.preset_mode.state`, suggesting some state-value translations may not apply as intended.

- **Planning Notes**
  - Confidence high on the specific `_none` risk in `switch.py` (`device_status` description) because both the code and translations leave no non-None naming source.
  - Capability comparison confidence high: pyvesync 3.3.3 method surfaces are directly enumerated from the extracted library under `/tmp/pyvesync_src_333`.

## Addendum (2025-12-13): Confirmed pyvesync 3.3.3 state fields + HA mapping corrections

- **Findings**
  - The earlier `_none` risk for `device_status` in the HA integration is no longer present in the current workspace: `custom_components/vesync/switch.py` now sets `name="Power"` and `translation_key="power"` for `key="device_status"`.
  - Confirmed pyvesync 3.3.3 `device.state` field names (and types) relevant to current HA entities:
    - Mute (fans): `state.mute_status` (str, `"on"`/`"off"`) and `state.mute_set_status` (str); HA switch should reflect `mute_status`, not `state.mute`.
    - Auto-stop (humidifiers): `state.automatic_stop_config` (bool) with convenience property `state.automatic_stop` (bool); HA switch should not read `state.auto_stop`.
    - Drying mode (humidifiers): `state.drying_mode_status` (str) with convenience properties `state.drying_mode_state` (str|None) and `state.drying_mode_enabled` (bool); HA switch should not read `state.drying_mode`.
    - Light detection (purifiers): `state.light_detection_switch` (str, `"on"`/`"off"`); pyvesync also keeps a deprecated boolean helper `state.light_detection` (bool) derived from `light_detection_switch`.
    - Vertical oscillation (fans): `state.vertical_oscillation_status` (str, `"on"`/`"off"`).
    - Horizontal oscillation (fans): `state.horizontal_oscillation_status` (str, `"on"`/`"off"`).
  - Purifier auto preference is readable and controllable in pyvesync 3.3.3:
    - Current preference: `device.state.auto_preference_type` (str|None) is populated during updates and after successful `set_auto_preference(...)`.
    - Supported options: `device.auto_preferences` (list[str]) is populated from device maps; in pyvesync’s built-in maps this is consistently `default`, `efficient`, `quiet` (note: `unknown` exists as an enum value but is not a supported preference choice).

- **Evidence**
  - Fan mute + oscillation state fields: `/tmp/pyvesync_src_333/pyvesync/base_devices/fan_base.py` (`FanState.__slots__` includes `mute_status`, `mute_set_status`, `vertical_oscillation_status`, `horizontal_oscillation_status`; `FanState` starts around line 24).
  - Fan mute state is populated from API responses: `/tmp/pyvesync_src_333/pyvesync/devices/vesyncfan.py` (sets `self.state.mute_status` and `self.state.mute_set_status` around lines 46–47).
  - Humidifier auto-stop + drying-mode fields: `/tmp/pyvesync_src_333/pyvesync/base_devices/humidifier_base.py` (`HumidifierState` documents `automatic_stop_config` and `drying_mode_status` around lines 28–37 and exposes `automatic_stop`/`drying_mode_enabled` properties around lines 123–180).
  - Purifier light detection + auto preference fields: `/tmp/pyvesync_src_333/pyvesync/base_devices/purifier_base.py` (`PurifierState.__slots__` includes `light_detection_switch` and `auto_preference_type` around lines 69–95).
  - Auto preference option strings: `/tmp/pyvesync_src_333/pyvesync/const.py` defines `PurifierAutoPreference.DEFAULT='default'`, `EFFICIENT='efficient'`, `QUIET='quiet'` around lines 438–451.
  - Auto preference supported option set per model: `/tmp/pyvesync_src_333/pyvesync/device_map.py` shows `auto_preferences=[PurifierAutoPreference.DEFAULT, PurifierAutoPreference.EFFICIENT, PurifierAutoPreference.QUIET]` for multiple purifier maps (e.g., around lines 758–762).
  - Auto preference state is updated on set: `/tmp/pyvesync_src_333/pyvesync/devices/vesyncpurifier.py` sets `self.state.auto_preference_type = preference` after successful API call (e.g., around lines 218–229 and again around lines 648–675 depending on class/model).

- **Gaps / Questions**
  - Some purifiers may report `state.auto_preference_type=None` until at least one refresh; HA select should tolerate `None` (unknown/unavailable) cleanly.
  - Room size (`state.auto_room_size`) is writable via `set_auto_preference(..., room_size=...)`; decide whether to expose this as a separate HA `number` or leave at pyvesync defaults.

- **Planning Notes**
  - Exact HA mapping fixes suggested by this addendum:
    - `custom_components/vesync/switch.py`: update the incorrect `is_on` lambdas:
      - `drying_mode`: `is_on=lambda d: bool(rgetattr(d, "state.drying_mode_enabled"))` (or `rgetattr(d, "state.drying_mode_status") == "on"`).
      - `mute`: `is_on=lambda d: rgetattr(d, "state.mute_status") == "on"`.
      - `auto_stop`: `is_on=lambda d: bool(rgetattr(d, "state.automatic_stop"))` (or `bool(rgetattr(d, "state.automatic_stop_config"))`).
    - `custom_components/vesync/select.py`: add a purifier `select` for auto preference:
      - `exists_fn=lambda d: is_purifier(d) and hasattr(d, "set_auto_preference") and bool(getattr(d, "auto_preferences", None))`
      - `options=["default", "efficient", "quiet"]` (static) or (preferred) use a dynamic options property sourced from `d.auto_preferences`.
      - `current_option_fn=lambda d: d.state.auto_preference_type`
      - `select_option_fn=lambda d, v: d.set_auto_preference(v)`
    - `custom_components/vesync/switch.py`: consider switching post-command updates from `schedule_update_ha_state()` to `await coordinator.async_request_refresh()` for immediate consistency with coordinator-driven polling.
