# VeSync Custom Component

This repository includes a forked/maintained VeSync integration under `custom_components/vesync`.

## Dependency / version pin

This integration is pinned to `pyvesync==3.3.3` (see `custom_components/vesync/manifest.json`).
Entity/service availability and some failure modes depend on that exact library version and the upstream VeSync cloud API.

## Entities

The integration exposes capabilities as standard Home Assistant entity platforms when supported by the specific device model:

- **`fan`**: fans and air purifiers (power, speed/percentage, preset modes, oscillation when supported).
- **`humidifier`**: humidifiers (power, mode, target humidity).
- **`climate`**: thermostats (HVAC mode, target temperature, fan mode).
- **`light`**: bulbs/dimmers and dimmer wall switches; supported wall switches may also expose an RGB **backlight color** light entity.
- **`switch`**: outlet/wall-switch power, plus capability-gated toggles (e.g., display, display type, child lock, mute, light detection, oscillation, drying mode, auto stop, indicator light, backlight). Air fryers may also expose a `cooking_status` switch as a pause/resume convenience (not a true power switch).
- **`sensor`**: air quality metrics (AQ/PM/VOC/CO₂/temp/humidity), filter life, outlet power/voltage/energy histories, plus air fryer cook status/current temperature/time remaining.
- **`binary_sensor`**: humidifier water/tank problem flags and purifier filter door open (when reported by the device).
- **`number`**: humidifier mist level, warm mist level (capability-gated), timer minutes (capability-gated), and fan oscillation range coordinates (capability-gated).
- **`select`**: night light level (humidifier/purifier/outlet models that support it) and purifier auto preference (capability-gated).
- **`button`**: filter reset (capability-gated) and air fryer pause/resume/end controls (capability-gated).
- **`update`**: firmware versions (reporting only).

For a device-by-device capability mapping against the pinned library version, see:

- [vesync-pyvesync-coverage.md](vesync-pyvesync-coverage.md)

## Key behavior

- Entities request a coordinator refresh after commands so UI state updates promptly.
- Config entry setup performs an initial coordinator refresh to avoid "unknown" states on startup.
- Energy readings (when supported) are refreshed by a separate coordinator on a slower schedule; the first energy refresh is started in the background during setup.
- Runtime data is scoped by config entry id to keep unload/reload idempotent.
- Config entry minor version `7` normalizes firmware update entity `unique_id`s to the `*-firmware` scheme (preventing collisions with primary entities) and fixes legacy binary_sensor unique_id suffixes.
- Config entry minor version `8` cleans up legacy `binary_sensor` entity_id collisions created before translations existed (e.g. duplicate `*_problem` / `*_problem_2` are renamed to deterministic suffixes).

## Scope decisions

- **Device families**: This custom component tracks the pinned `pyvesync==3.3.3` capability set and intentionally includes device categories that the official Home Assistant `vesync` integration may omit (notably **kitchen devices / air fryers**). The supported surface is audited in [vesync-pyvesync-coverage.md](vesync-pyvesync-coverage.md).
- **Authentication**: The integration continues to use the Home Assistant config entry username/password flow and calls `VeSync.login()` during setup. Token persistence helpers (if available upstream) are intentionally not used here to avoid introducing new storage behavior or configuration requirements.

## Services

- `vesync.update_devices`
  - Discovers newly added VeSync devices across all loaded config entries and forwards them to platform discovery.
  - Discovery considers additional pyvesync device buckets (e.g., thermostats and kitchen devices) so newly added devices are detected consistently.
  - Service schemas (fields, selectors, targets) live in [custom_components/vesync/services.yaml](../../custom_components/vesync/services.yaml).

The additional services below are **device-targeted** (recommended HA pattern). In YAML automations/scripts, pass the device target via `target.device_id`.

Examples:

```yaml
# Discover newly added devices (no target)
service: vesync.update_devices
```

```yaml
# Start an air fryer cook cycle (supported models only)
service: vesync.fryer_cook
target:
  device_id: 0123456789abcdef0123456789abcdef
data:
  temperature: 400
  time: 12
```

```yaml
# Lock a thermostat (PIN required when locking)
service: vesync.thermostat_set_lock
target:
  device_id: 0123456789abcdef0123456789abcdef
data:
  locked: true
  pin: '1234'
```

- Fryer services (supported models only):
  - `vesync.fryer_cook` (temperature + time)
  - `vesync.fryer_set_preheat` (temperature + cook_time)
  - `vesync.fryer_cook_from_preheat`

  Parameters (see `services.yaml` for selectors/ranges):
  - `temperature`: integer temperature value as expected by the device
  - `time` / `cook_time`: integer minutes

- Thermostat services (supported models only):
  - `vesync.thermostat_cancel_hold`
  - `vesync.thermostat_set_lock` (locked + pin when locking)
  - `vesync.thermostat_set_eco_type` (eco_type)

  `eco_type` options (pinned to `pyvesync==3.3.3`):
  - `comfort_second`, `comfort_first`, `balance`, `eco_first`, `eco_second`

## Troubleshooting

- Enable debug logging for the integration and `pyvesync` in [packages/logger.yaml](../../packages/logger.yaml).
- Typical validation loop:
  - `pnpm home-assistant services call homeassistant restart -d '{}'`
  - Wait for API to come back: `pnpm home-assistant api info`
  - Reload entities/config: `pnpm reload`
  - Logs (Supervisor): `pnpm home-assistant raw request GET /api/hassio/core/logs --text | grep -i -E "vesync|pyvesync|custom_components\.vesync"`

If fetching logs times out (default request timeout is 10s), increase it via:

- Env var: `HOME_ASSISTANT_TIMEOUT_MS=60000 pnpm home-assistant raw request GET /api/hassio/core/logs --text`
- CLI flag: `pnpm home-assistant --timeout 60000 raw request GET /api/hassio/core/logs --text`

### Diagnostics

Home Assistant diagnostics for this integration are intended to be safe to share when filing issues:

- Config entry `data` (credentials) is redacted.
- Device diagnostics include a curated snapshot of the pyvesync device and its `state` (JSON-serializable), with common sensitive keys (tokens, uuids, MACs, etc.) redacted.

### Verification (surface audit)

This repo includes an offline audit script that reads Home Assistant registry data from `.storage/` and generates a normalized inventory and an optional deterministic parity (PASS/FAIL) report.

- Script: [scripts/vesync_audit.py](../../scripts/vesync_audit.py)
- Runtime inventory (from this workspace): [docs/custom-components/vesync-surface.md](vesync-surface.md)
- Parity report (from this workspace): [docs/custom-components/vesync-parity.md](vesync-parity.md)

Generate the inventory from the repo root:

```bash
python scripts/vesync_audit.py \
  --out-json /tmp/vesync_runtime_inventory.json \
  --out-md docs/custom-components/vesync-surface.md
```

Generate the parity report (compares code/services against the machine-readable manifest in [vesync-pyvesync-coverage.md](vesync-pyvesync-coverage.md)):

```bash
python scripts/vesync_audit.py \
  --compare \
  --out-compare-json docs/custom-components/vesync-parity.json \
  --out-compare-md docs/custom-components/vesync-parity.md
```

### Common `pyvesync`-side errors

The VeSync API is cloud-backed and `pyvesync` may raise errors that are not caused by Home Assistant itself.
This integration surfaces the error messages where possible, but cannot always recover automatically.

- **Login/auth errors** (e.g., `VeSyncLoginError`, or repeated “invalid credentials” failures)
  - Re-check username/password, and confirm you can sign in via the VeSync mobile app.
  - If you recently changed your password, re-auth/reload the integration to ensure HA is using the new credentials.
  - Re-auth UX note: the re-auth confirmation form should not show an error banner until after a failed submit.

- **“Invalid response format” / unexpected payloads**
  - This commonly indicates the VeSync cloud returned an unexpected response shape (empty body, HTML, partial JSON, API change, transient outage).
  - Suggested next steps:
    - Wait a few minutes and try again (cloud/API issues can be transient).
    - Restart Home Assistant, then review debug logs for the first occurrence.
    - If it persists, capture redacted logs (no credentials/tokens) and include device model + time window when filing an issue.
  - Because this repo pins `pyvesync==3.3.3`, persistent API-shape changes may require a future pin bump and integration adjustments rather than a local config tweak.

- **Humidifier “bypassV2” noise** (`Error processing bypass V2 API response result`)
  - Some humidifier models intermittently trigger this pyvesync-side error during detail fetches.
  - This custom integration filters that specific pyvesync error log message and suppresses that specific exception from `get_details()` to keep logs clean while allowing normal recovery.
  - If you’re diagnosing humidifier update issues, enable debug logs and look for adjacent `custom_components.vesync` warnings/errors around the same timestamp.

- **Service/entity calls fail but state doesn’t update**
  - Many controls return a boolean plus a `last_response.message` from the cloud API. If an action appears to succeed but the UI doesn’t update, check logs and confirm a coordinator refresh ran (or run `vesync.update_devices` if you recently added devices).

## Notes on warm mist

- The integration reads warm mist level from `device.state.warm_mist_level` (as exposed by `pyvesync`).
- Warm mist setters vary by `pyvesync` version; this repo supports `set_warm_level` (and falls back to `set_warm_mist` if present).
