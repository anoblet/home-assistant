# VeSync → pyvesync coverage (pinned: `pyvesync==3.3.3`)

This repo includes a forked/maintained VeSync integration under `custom_components/vesync`.

The goal of this document is to make “feature coverage” auditable: for each `pyvesync` device class, list the primary state fields and control methods exposed by the library, and where (or whether) the Home Assistant integration exposes them.

Notes:

- Mapping is intentionally conservative and tied to the pinned `pyvesync==3.3.3` requirement.
- Some `pyvesync` capabilities exist but do not map cleanly to Home Assistant entity models; those are explicitly called out as “not exposed”.

## Capability coverage summary (pinned: `pyvesync==3.3.3`)

This custom integration aims to expose all *feasible* `pyvesync==3.3.3` capabilities in a Home Assistant-friendly way while keeping the external “surface contract” stable (platforms + services + unique_id scheme).

| pyvesync area / device type | Home Assistant exposure | Notes |
| --- | --- | --- |
| Device discovery | Service: `vesync.update_devices` | Iterates all loaded config entries; dispatch signals are scoped per entry to avoid cross-entry churn. |
| Firmware availability | `update` entities | Firmware checks run in the background and trigger a refresh so `update` entities reflect availability promptly. |
| Fans / Purifiers / Humidifiers / Outlets / Wall switches / Bulbs | Standard entities (`fan`, `humidifier`, `switch`, `sensor`, `number`, `select`, `light`, etc.) | Capability-gated; methods/fields are mapped where HA semantics are stable. |
| Air fryers (Cosori) | Services: `vesync.fryer_*` + entities (`button`/`sensor`) | Exposes non-standard controls without creating excessive entities; each service call requests a refresh. |
| Thermostats | `climate` entities + services: `vesync.thermostat_*` | Core HVAC control maps to `climate`; additional discrete actions exposed via services. |

**Not exposed (intentionally)**

- Thermostat schedule/program editing and other routine programming: not exposed because the pinned library does not provide a stable, supported programming API in `pyvesync==3.3.3`.
- Credential persistence helpers exposed by `pyvesync` are not used; Home Assistant config entries/reauth handle authentication lifecycle.

## Verification (runtime surface audit)

To make “no missing/erroneous entities” reviewable against a real instance, this repo includes a small audit script that generates a runtime inventory from Home Assistant’s registry files under `.storage`.

- Script: [scripts/vesync_audit.py](../../scripts/vesync_audit.py)
- Generated report (from this workspace): [docs/custom-components/vesync-surface.md](vesync-surface.md)

Run it from the repo root:

```bash
python scripts/vesync_audit.py \
  --out-json /tmp/vesync_runtime_inventory.json \
  --out-md docs/custom-components/vesync-surface.md
```

The output is intended to be safe to store in-repo: it does not include the VeSync config entry `data` payload (credentials/tokens).

To mechanically verify that the integration surface matches this document, the audit script also supports a deterministic comparator mode.

- Parity report (from this workspace): [docs/custom-components/vesync-parity.md](vesync-parity.md)
- Parity report (machine-readable): [docs/custom-components/vesync-parity.json](vesync-parity.json)

Regenerate the parity artifacts from the repo root:

```bash
python scripts/vesync_audit.py \
  --compare \
  --out-compare-json docs/custom-components/vesync-parity.json \
  --out-compare-md docs/custom-components/vesync-parity.md
```

## Expected surface manifest (machine-readable)

This block is the canonical, parseable “expected surface” used by audit tooling. Keep it aligned with the “Home Assistant exposure” sections below; do not add new claims here without also updating the narrative mapping.

```json
{
  "vesync_expected_surface": {
    "platforms": [
      "binary_sensor",
      "button",
      "climate",
      "fan",
      "humidifier",
      "light",
      "number",
      "select",
      "sensor",
      "switch",
      "update"
    ],
    "services": [
      "fryer_cook",
      "fryer_cook_from_preheat",
      "fryer_set_preheat",
      "thermostat_cancel_hold",
      "thermostat_set_eco_type",
      "thermostat_set_lock",
      "update_devices"
    ],
    "device_classes": {
      "VeSyncFanBase": { "platforms": ["fan", "number", "switch"] },
      "VeSyncPurifier": {
        "platforms": ["binary_sensor", "button", "fan", "number", "select", "sensor", "switch"]
      },
      "VeSyncHumidifier": {
        "platforms": ["binary_sensor", "humidifier", "number", "select", "sensor", "switch"]
      },
      "VeSyncOutlet": { "platforms": ["number", "select", "sensor", "switch"] },
      "VeSyncWallSwitch": { "platforms": ["light", "number", "switch"] },
      "VeSyncBulb": { "platforms": ["light", "number"] },
      "VeSyncThermostat": { "platforms": ["climate"] },
      "VeSyncFryer": { "platforms": ["button", "sensor"] }
    },
    "firmware": { "platforms": ["update"] }
  }
}
```

## Identity / entity keys

- Base unique id is derived from `device.cid` (or `cid + sub_device_no` when present).
- Home Assistant entities generally follow: `<base_unique_id>-<entity_key>`.
- Firmware update entities use: `<base_unique_id>-firmware`.

## Device class coverage

For service action field definitions (targets, selectors, valid ranges), see:

- [custom_components/vesync/services.yaml](../../custom_components/vesync/services.yaml)

### `VeSyncFanBase` (fans)

**Library state (key fields)**

From `pyvesync/base_devices/fan_base.py` (`FanState`):

State attributes (from `FanState.__slots__`):

- `child_lock`
- `display_set_status`, `display_status`, `displaying_type`
- `fan_level`, `fan_set_level`
- `horizontal_oscillation_status`, `vertical_oscillation_status`, `oscillation_set_status`, `oscillation_status`
- `oscillation_coordinates`, `oscillation_range`
- `humidity`, `temperature`, `thermal_comfort`
- `mode`
- `mute_set_status`, `mute_status`
- `sleep_change_fan_level`, `sleep_fallasleep_remain`, `sleep_oscillation_switch`, `sleep_preference_type`

**Library controls (public methods)**

From `pyvesync/base_devices/fan_base.py` (`VeSyncFanBase`):

- `set_mode(mode: str) -> bool`
- `set_fan_speed(speed: int | None = None) -> bool`
- Mode helpers: `set_auto_mode()`, `set_advanced_sleep_mode()`, `set_sleep_mode()`, `set_manual_mode()`, `set_normal_mode()`, `set_turbo_mode()`
- Oscillation helpers: `toggle_oscillation(toggle: bool)`, `toggle_vertical_oscillation(toggle: bool)`, `toggle_horizontal_oscillation(toggle: bool)`
- Oscillation range helpers: `set_vertical_oscillation_range(*, top: int = 0, bottom: int = 0)`, `set_horizontal_oscillation_range(*, left: int = 0, right: int = 0)`
- Sound/display helpers: `toggle_mute(toggle: bool)`, `toggle_display(toggle: bool)`, `toggle_displaying_type(toggle: bool)`

Implemented on concrete fan devices in `pyvesync/devices/vesyncfan.py` (e.g., `VeSyncTowerFan`, `VeSyncPedestalFan`):

- `get_details() -> None`
- `toggle_switch(toggle: bool | None = None) -> bool`
- Timer helpers (models that support them): `get_timer() -> None`, `set_timer(duration: int, action: str | None = None) -> bool`, `clear_timer() -> bool`

**Home Assistant exposure**

- `fan` platform: on/off (`toggle_switch`), percentage (`set_fan_speed`), preset modes (`set_mode`), oscillation (when supported).
- `switch` platform: mute/display/display type + oscillation toggles (capability-gated by `device.state.*` and `device.supports_*`).
- `number` platform: timer minutes (where `set_timer`/`clear_timer` exist) and oscillation range coordinates (when `supports_set_oscillation_range`).

### `VeSyncPurifier` (air purifiers)

**Library state (key fields)**

From `pyvesync/base_devices/purifier_base.py` (`PurifierState`):

State attributes (from `PurifierState.__slots__`):

- `mode`
- `fan_level`, `fan_set_level`
- `filter_life`, `filter_open_state`
- `auto_preference_type`, `auto_room_size`
- Air quality fields (capability-gated): `_air_quality_level` (exposed via `state.air_quality_level`), `pm25`, `pm1`, `pm10`, `aq_percent`, `voc`, `co2`, `temperature`, `humidity`
- Feature toggles (capability-gated): `child_lock`, `display_status`, `display_set_status`, `display_forever`, `light_detection_switch`, `light_detection_status`, `nightlight_status`, `nightlight_brightness`
- `fan_rotate_angle`

**Library controls (public methods)**

From `pyvesync/base_devices/purifier_base.py` (`VeSyncPurifier`):

- `set_mode(mode: str) -> bool`
- `set_fan_speed(speed: int | None = None) -> bool`
- Mode helpers: `set_auto_mode()`, `set_sleep_mode()`, `set_manual_mode()`, `set_turbo_mode()`, `set_pet_mode()`
- Display: `toggle_display(mode: bool) -> bool` (+ helpers `turn_on_display()`, `turn_off_display()`)
- Nightlight: `set_nightlight_mode(mode: str) -> bool` (+ helpers `set_nightlight_dim()`, `turn_on_nightlight()`, `turn_off_nightlight()`)
- Child lock: `toggle_child_lock(toggle: bool | None = None) -> bool` (+ helpers `turn_on_child_lock()`, `turn_off_child_lock()`)
- Auto preference: `set_auto_preference(preference: str, room_size: int = 800) -> bool`
- Light detection (when supported): `toggle_light_detection(toggle: bool | None = None) -> bool` (+ helpers `turn_on_light_detection()`, `turn_off_light_detection()`)
- Filter reset (when supported): `reset_filter() -> bool`

Common concrete implementations in `pyvesync/devices/vesyncpurifier.py` also include:

- `get_details() -> None`
- `toggle_switch(toggle: bool | None = None) -> bool`
- Timer helpers (models that support them): `get_timer() -> Timer | None`, `set_timer(duration: int, action: str | None = None) -> bool`, `clear_timer() -> bool`

**Home Assistant exposure**

- `fan` platform: purifier power + speed + preset modes (mode/speed methods).
- `sensor` platform: AQ/PM/VOC/CO₂/temp/humidity (capability-gated).
- `button` platform: filter reset (`reset_filter`).
- `binary_sensor` platform: filter door open (`state.filter_open_state`).
- `switch` platform: child lock / display / light detection (capability-gated).
- `select` platform: purifier nightlight mode (`set_nightlight_mode`) and auto preference (`set_auto_preference`) when supported.
- `number` platform: timer minutes (where `set_timer`/`clear_timer` exist).

### `VeSyncHumidifier` (humidifiers)

**Library state (key fields)**

From `pyvesync/base_devices/humidifier_base.py` (`HumidifierState`):

State attributes (from `HumidifierState.__slots__`):

- `mode`
- `humidity`, `temperature`
- `auto_target_humidity`
- Mist: `mist_level`, `mist_virtual_level`
- Warm mist (capability-gated): `warm_mist_enabled`, `warm_mist_level`
- Water/tank flags: `water_lacks`, `water_tank_lifted`
- Display/nightlight (capability-gated): `display_status`, `display_set_status`, `nightlight_status`, `nightlight_brightness`
- Automatic stop (capability-gated): `automatic_stop_config`, `auto_stop_target_reached`
- Drying mode (capability-gated): `drying_mode_status`, `drying_mode_level`, `drying_mode_time_remain`, `drying_mode_auto_switch`
- Other capability-gated fields: `auto_preference`, `filter_life`, `humidity_high`, `child_lock`

**Library controls (public methods)**

From `pyvesync/base_devices/humidifier_base.py` (`VeSyncHumidifier`):

- `set_mode(mode: str) -> bool`
- `set_mist_level(level: int) -> bool`
- `set_humidity(humidity: int) -> bool`
- Display: `toggle_display(toggle: bool) -> bool`
- Automatic stop: `toggle_automatic_stop(toggle: bool | None = None) -> bool`
- Nightlight: `toggle_nightlight(toggle: bool | None = None) -> bool`, `set_nightlight_brightness(brightness: int) -> bool`
- Warm mist: `set_warm_level(warm_level: int) -> bool`
- Drying mode: `toggle_drying_mode(toggle: bool | None = None) -> bool`
- Mode helpers: `set_auto_mode()`, `set_manual_mode()`, `set_sleep_mode()`

Common concrete implementations in `pyvesync/devices/vesynchumidifier.py` also include:

- `get_details() -> None`
- `toggle_switch(toggle: bool | None = None) -> bool`
- Timer helpers (models that support them): `get_timer() -> Timer | None`, `set_timer(duration: int, action: str | None = None) -> bool`, `clear_timer() -> bool`

**Integration note (known library quirk)**

Some humidifier models intermittently trigger a pyvesync-side failure during `get_details()` that includes the message
`Error processing bypass V2 API response result`. This custom integration applies a narrow patch to:

- Filter that specific pyvesync error log message, and
- Suppress that specific exception from `get_details()` while re-raising other unexpected exceptions.

Implementation: [custom_components/vesync/patches.py](../../custom_components/vesync/patches.py)

**Home Assistant exposure**

- `humidifier` platform: on/off (`toggle_switch`), modes (`set_mode`), target humidity (`set_humidity`).
- `number` platform: mist level (`set_mist_level`), warm mist level (`set_warm_level`), timer minutes (`set_timer`/`clear_timer`).
- `sensor` platform: humidity/temperature.
- `binary_sensor` platform: low water / tank lifted.
- `select` platform: nightlight brightness (via `set_nightlight_brightness`).
- `switch` platform: display / drying mode / automatic stop (capability-gated).

### `VeSyncOutlet` (smart outlets / plugs)

**Library state (key fields)**

From `pyvesync/base_devices/outlet_base.py` (`OutletState`):

State attributes (from `OutletState.__slots__`):

- Energy monitoring/history: `power`, `energy`, `voltage`, `current`, `weekly_history`, `monthly_history`, `yearly_history`
- Nightlight (capability-gated): `nightlight_status`, `nightlight_brightness`, `nightlight_automode`
- Device-specific protection fields: `protectionStatus`, `voltageUpperThreshold`, `currentUpperThreshold`

**Library controls (public methods)**

From `pyvesync/devices/vesyncoutlet.py` (common across outlet models):

- `get_details() -> None`
- `toggle_switch(toggle: bool | None = None) -> bool`
- Timer helpers (models that support them): `get_timer() -> Timer | None`, `set_timer(duration: int, action: str | None = None) -> bool`, `clear_timer() -> bool`

From `pyvesync/base_devices/outlet_base.py` (`VeSyncOutlet`):

- Energy history: `get_weekly_energy()`, `get_monthly_energy()`, `get_yearly_energy()`, `update_energy()`
- Nightlight (capability-gated): `set_nightlight_state(mode: str) -> bool`, `set_nightlight_auto() -> bool`, `turn_on_nightlight() -> bool`, `turn_off_nightlight() -> bool`

**Home Assistant exposure**

- `switch` platform: outlet power (`toggle_switch`).
- `sensor` platform: power/voltage/current/energy + history-derived totals (capability-gated).
- `select` platform: nightlight mode (when supported).
- `number` platform: timer minutes (where `set_timer`/`clear_timer` exist).

### `VeSyncWallSwitch` / `VeSyncSwitch` (wall switches)

**Library state (key fields)**

From `pyvesync/base_devices/switch_base.py` (`SwitchState`):

State attributes (from `SwitchState.__slots__`):

- `brightness`
- `backlight_status`, `backlight_color`
- `indicator_status`

**Library controls (public methods)**

From `pyvesync/base_devices/switch_base.py` (`VeSyncSwitch`):

- Indicator: `toggle_indicator_light(toggle: bool | None = None) -> bool`
- Backlight: `set_backlight_status(status: bool, red: int | None = None, green: int | None = None, blue: int | None = None) -> bool` and `set_backlight_color(red: int, green: int, blue: int) -> bool`
- Dimmer brightness (dimmer models): `set_brightness(brightness: int) -> bool`

From `pyvesync/devices/vesyncswitch.py`:

- Wall switch (`VeSyncWallSwitch`): `get_details()`, `toggle_switch(toggle: bool | None = None)`, timer helpers `get_timer()`, `set_timer(duration: int, action: str | None = None)`, `clear_timer()`
- Dimmer switch (`VeSyncDimmerSwitch`): `get_details()`, `toggle_switch(toggle: bool | None = None)`, `toggle_indicator_light(toggle: bool | None = None)`, `set_backlight_status(...)`, `set_brightness(brightness: int)`, timer helpers `get_timer()`, `set_timer(...)`, `clear_timer()`

**Home Assistant exposure**

- `switch` platform: main power and supported toggles (indicator/backlight, etc.).
- `light` platform: dimmer switch brightness (where the integration models the device as a light).
- `light` platform: backlight RGB color control (when `supports_backlight_color`).
- `number` platform: timer minutes (where `set_timer`/`clear_timer` exist).

### `VeSyncBulb` (bulbs / dimmable lighting)

**Library state (key fields)**

From `pyvesync/base_devices/bulb_base.py` (`BulbState`):

State attributes (from `BulbState.__slots__`):

- `color_mode`, `color_modes`
- `_brightness` (exposed via `state.brightness`)
- `_color_temp` (exposed via `state.color_temp` / `state.color_temp_kelvin`)
- `_color` (exposed via `state.color`, `state.hsv`, `state.rgb`)

**Library controls (public methods)**

From `pyvesync/base_devices/bulb_base.py` (`VeSyncBulb`):

- `set_brightness(brightness: int) -> bool`
- `set_color_temp(color_temp: int) -> bool`
- `set_rgb(red: float, green: float, blue: float) -> bool`
- `set_hsv(hue: float, saturation: float, value: float) -> bool`
- `set_white_mode() -> bool`
- `set_color_mode(color_mode: str) -> bool`

Common concrete implementations in `pyvesync/devices/vesyncbulb.py` also include:

- `get_details() -> None`
- `toggle_switch(toggle: bool | None = None) -> bool`
- Some models implement timer helpers: `get_timer()`, `set_timer(duration: int, action: str | None = None)`, `clear_timer()`
- Some models implement granular setters: `set_color_hue(...)`, `set_color_saturation(...)`, `set_color_value(...)`, and/or `set_status(...)`

**Home Assistant exposure**

- `light` platform: on/off + brightness + color temp + HS color (capability-gated).
- `number` platform: timer minutes (where `set_timer`/`clear_timer` exist).

### `VeSyncThermostat` (thermostats)

**Library state (examples)**

- `device.state.temperature`
- `device.state.work_mode` (enum)
- `device.state.fan_mode` (enum)
- Heat/cool target temps (mode-dependent)
- Running flags such as `is_heating` / `is_cooling` / `is_running`

**Library controls (examples)**

- `set_mode(ThermostatWorkModes)`
- `set_fan_mode(ThermostatFanModes)`
- Temperature setters (pyvesync 3.3.3 `VeSyncAuraThermostat`):
  - `set_heat_to_temp(temperature: float)`
  - `set_cool_to_temp(temperature: float)`
  - `set_temp_point(temperature: float)`
- Hold/lock/eco controls (pyvesync 3.3.3 `VeSyncAuraThermostat`):
  - `cancel_hold()`
  - `toggle_lock(toggle: bool, pin: int | str | None = None)`
  - `set_eco_type(eco_type: ThermostatEcoTypes)`

**Home Assistant exposure**

- `climate` platform: hvac modes (from `supported_work_modes`), hvac action (heat/cool/fan/idle), fan modes, current temperature, and target temperature.

**Additional control exposure (services)**

- `vesync.thermostat_cancel_hold`
- `vesync.thermostat_set_lock`
- `vesync.thermostat_set_eco_type`

**Not exposed (by design / not cleanly representable)**

- `pyvesync==3.3.3` reports schedule/routine _state_ (e.g. `state.schedule_or_hold`, `state.routines`) but does not expose public schedule/routine programming methods (verified by inspecting the `pyvesync==3.3.3` source in `pyvesync/devices/vesyncthermostat.py`); this repo therefore does not expose schedule/routine programming.

### `VeSyncFryer` (air fryer / kitchen device)

**Library state (examples)**

- `device.state.cook_status`
- `device.state.current_temp`
- `device.state.cook_time_remaining`
- Other model-provided cook program fields

**Library controls (examples)**

- `pause()`
- `resume()`
- `end()`
- `cook(set_temp: int, set_time: int)` (parameterized; minutes)
- `set_preheat(target_temp: int, cook_time: int)`
- `cook_from_preheat()`

**Home Assistant exposure**

- `sensor` platform: core fryer state values (derived from `device.state`).
- `button` platform: pause/resume/end.

**Additional control exposure (services)**

- `vesync.fryer_cook` (temp + time)
- `vesync.fryer_set_preheat` (temp + cook_time)
- `vesync.fryer_cook_from_preheat`

## Firmware update coverage

All device classes expose firmware metadata via:

- `device.current_firm_version`
- `device.latest_firm_version`

Home Assistant exposure:

- `update` platform provides a firmware update entity per device with unique id `*-firmware`.
