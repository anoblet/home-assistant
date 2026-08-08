# Changelog

## 2026-08-06

- Fixed the bedroom AC off-on-vacancy behavior: `packages/areas/bedroom/presence/off/thermostat.yaml` now calls `climate.turn_off` on both thermostats after a 15 s presence-off hold (the old 1-minute hold with setpoint-only actions never fired, so the AC never stopped), and `packages/areas/bedroom/script/air_conditioner/off.yaml` bounds the physical `PowerToggle` debounce to 30 s via `timeout: '00:00:30'` (was an unbounded 300 s wait).
- Updated `docs/automations.md` with Example 6 documenting the presence on/off bedroom climate chain (15 s hold → `climate.turn_off` → template switch → debounced Harmony `PowerToggle`; presence on → `climate.turn_on` resumes at the current setpoint), a State Trigger example reference, a zone-leave cross-reference in Example 3, and a Troubleshooting note on unsatisfiable `for:` holds.

## 2026-04-26

- Added the existing Motion / Occupancy view to the Presence dashboard by including `includes/lovelace/views/motion/index.yaml` in `includes/lovelace/dashboards/presence.yaml`, keeping the existing `path: motion` route and renaming the view title for clarity.

## 2026-04-20

- Split the five background music helpers with no `initial` values into `packages/shared/background_music_input.yaml` under `shared_background_music_input`, leaving `packages/shared/background_music.yaml` focused on Google Assistant exposure, the script, and the weekday automations. The script and automations still read the same helper entity ids at runtime.
- Documented the forward-looking rule that package-owned input helpers belong in a separate standalone package file, typically using a feature-scoped `_input` suffix when one feature spans multiple input domains.

## 2026-04-19

- Simplified the shared SQM toggle loop so it rereads helper timing bounds each cycle, normalizes inverted min/max pairs, uses inclusive second-granularity random windows, and drops warning-level trace logging from the normal enable/disable path.
- Corrected `docs/automations.md` so its package-layout and worked-example references match the active six-directory taxonomy and current package keys.

## 2026-04-14

- Documented the room configuration subview entities-card standard for the Rooms dashboard: one built-in `entities` card per concern section, with the authoritative guidance kept aligned across the repo instructions and structure guidance.

## 2026-04-13

- Documented the bathroom Lovelace polish changes: shortened labels in the Bathroom configuration subview, moved the Configuration tile onto its own final row, and improved select/dropdown contrast in the active Unicorn Vampire theme.

## 2026-04-10

- Documented the completed bathroom helper and subview work: helper-backed bathroom timing and lighting tunables, helper-driven Adaptive Lighting sync, and the Bathroom `Configuration` subview on the Rooms dashboard.

## 2026-04-06

- Documented the living room TV refactor pattern: split multi-responsibility area automations into nested trigger directories with one concern per file, with the living room TV `on/` and `off/` automations as the reference example.

## 2026-04-05

- Documented two Home Assistant validation lessons from the SQM helper session: use `pnpm home-assistant error-log` when the Supervisor core-log endpoint is unavailable, and do not assume helper `initial` value changes overwrite persisted live helper state after `pnpm reload`.
- Documented that SQM dashboards and other entity references should use the live `_2` SQM toggle automation ids until the stale unsuffixed restored duplicates are cleaned up from the entity registry.

## 2026-03-23

### Package Reorganization (Phase 2)

Completed migration of `packages/domains/` and `packages/common/` into the active taxonomy. All 315 YAML package files now reside exclusively under the six active directories.

#### Structural changes

- **Migrated `packages/domains/`** — 42 files moved to `areas/` (21), `integrations/` (6), and `shared/` (36, including vacuum scripts and zone definitions).
- **Migrated `packages/common/`** — 4 presence-related files moved to `shared/presence/`.
- **Migrated root-level packages** — 16 YAML files at `packages/` root moved to `integrations/` (4), `shared/` (9), and `schedules/` (3).
- **Created `packages/integrations/`** and **`packages/shared/`** directories for cross-cutting configuration.
- **Renamed kebab-case directory** `carbon-dioxide/` → `carbon_dioxide/` under `areas/bedroom/climate/`.

#### Cleanup

- Removed 12 dead/orphaned files (commented-out, empty, invalid, or redirect stubs).
- Removed orphaned `includes/lovelace/dashboards.yaml` (not referenced by `configuration.yaml`).

#### Naming convention

- Renamed 63 top-level YAML keys to follow taxonomy-prefixed snake_case:
  - Area packages: `area_domain_feature` (e.g., `bedroom_script_cast_display`)
  - Integration packages: `integrations_name` (e.g., `integrations_adaptive_lighting`)
  - Shared packages: `shared_domain_feature` (e.g., `shared_vacuum_start`)
  - Schedule packages: `schedules_name` (e.g., `schedules_morning`)
- Zero key collisions across all 315 files.

#### Validation

- All 315 YAML files pass syntax validation.
- All 10 Lovelace dashboard `filename:` paths verified to point to existing include files.
- Zero stale cross-references to `packages/common/` or `packages/domains/`.

#### File distribution

| Directory       | Files   |
| --------------- | ------- |
| `areas/`        | 243     |
| `integrations/` | 10      |
| `people/`       | 6       |
| `reminders/`    | 3       |
| `schedules/`    | 4       |
| `shared/`       | 49      |
| **Total**       | **315** |

#### Deferred items

- Dashboard entrypoint filenames in `includes/lovelace/dashboards/` remain kebab-case (high risk, requires HA restart).
- Empty `domains/` and `common/` directory trees remain (terminal policy prevented `rmdir`; directories are inert).
- Pre-existing naming inconsistencies (`reminders/my_tasks.yaml` key, `living_room/blinds/blinds.yaml` redundancy) not in scope.

## 2026-03-22

- Updated repository documentation to reflect the phase-1 reorganization of `packages/` and `includes/lovelace/`.
- Documented the active package taxonomy, standardized Lovelace dashboard entrypoint filenames, and the validation caveat that dashboard path moves may require a Home Assistant restart.
- Clarified that `!include_dir_merge_named packages/` loads YAML recursively, so nested helper fragments should not live under active package owner folders unless they are intentional standalone package entries.
- Consolidated background music into a single inlined `packages/integrations/media_player/background_music/core.yaml` package entrypoint that owns the Google Assistant exposure, script behavior, and weekday automations while preserving the live script and automation ids.
- Retired the old `packages/shared/media/background_music.yaml` and empty `packages/integrations/plants/reminder.yaml` files out of the active package tree so they no longer load as exceptions.
- Reduced the remaining discoverability exception list to the legacy `packages/common/` subtree.
