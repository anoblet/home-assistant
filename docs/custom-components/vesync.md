# VeSync Custom Component

This repository includes a forked/maintained VeSync integration under `custom_components/vesync`.

## What it supports

- **Fans / air purifiers** via the Home Assistant Fan entity model.
- **Humidifiers** via the Home Assistant Humidifier entity model.
- Optional **warm mist level** control (when the device supports warm mist).

## Key behavior

- Entities request a coordinator refresh after commands so UI state updates promptly.
- Config entry setup performs an initial coordinator refresh to avoid "unknown" states on startup.

## Services

- `vesync.update_devices`
  - Discovers newly added VeSync devices and forwards them to platform discovery.
  - Service definition lives in [custom_components/vesync/services.yaml](../../custom_components/vesync/services.yaml).

## Troubleshooting

- Enable debug logging for the integration and `pyvesync` in [packages/logger.yaml](../../packages/logger.yaml).
- Typical validation loop:
  - `ha core restart`
  - `ha core logs --lines 500 | grep -i -E "vesync|pyvesync|custom_components\.vesync"`

## Notes on warm mist

- The integration reads warm mist level from `device.state.warm_mist_level` (as exposed by `pyvesync`).
- Warm mist setters vary by `pyvesync` version; this repo supports `set_warm_level` (and falls back to `set_warm_mist` if present).

## Extended Features

The integration now exposes additional controls for supported devices:

- **Timer**: A `number` entity allowing you to set the device timer (0-1440 minutes).
- **Vertical Oscillation**: A `switch` entity to toggle vertical oscillation.
- **Drying Mode**: A `switch` entity to toggle drying mode.
- **Mute**: A `switch` entity to mute/unmute device sounds.
- **Auto Stop**: A `switch` entity to toggle the automatic stop feature.

These entities will appear automatically if the underlying device supports the feature.
