# Includes and packages audit

Audit date: 2026-08-08

## Scope and result

- [x] Audited all 93 files under `includes/` and all 352 files under `packages/`.
  - [x] Traced package loading from `configuration.yaml` (`homeassistant.packages: !include_dir_merge_named packages/`).
  - [x] Inventoried package names, component keys, automation IDs, helper definitions, Lovelace dashboard registrations, and `!include` edges.
  - [x] Ran a live Home Assistant configuration check against Core 2026.8.1; the result was `valid`, with no errors or warnings.
  - [x] Found no duplicate package names or duplicate explicit automation IDs.
  - [x] Found no `mode: single`, empty condition lists, helper `initial` values, or notification services that violate the configured mobile target rule.
- [ ] Improve structure and maintainability in the prioritized areas below.
  - [ ] P0: settle and enforce the root-integration/package-file rule before moving files.
  - [ ] P1: consolidate package ownership and helper placement.
  - [ ] P1: remove or reconnect legacy Lovelace content.
  - [ ] P2: normalize YAML schema and add automated structural checks.

## Important package-loader constraint

- [ ] Interpret “root key” carefully when applying the requested file-layout rule.
  - [x] A package file loaded by `!include_dir_merge_named` has two distinct levels: the outer key is the **package name**, and keys beneath it are Home Assistant **integration/component keys**.
  - [x] Today, `packages/integrations/influxdb.yaml` is shaped as package `integrations_influxdb` containing component key `influxdb`.
  - [ ] Move it to `packages/influxdb.yaml` to match the requested discoverability rule, while retaining a valid package wrapper, for example:

    ```yaml
    integrations_influxdb:
      influxdb:
        # configuration
    ```

  - [ ] Do **not** rename the outer package key to `influxdb` while also nesting `influxdb:` beneath it; duplicate nesting is required semantically but would be confusing. Do **not** remove the wrapper either, because `host`, `port`, and similar options would then be interpreted as package component names and the package would be invalid.
  - [ ] If the intended rule is literally “the outer package key must be `influxdb`,” change the loader strategy first (for example, include a root integration file directly from `configuration.yaml`) rather than forcing direct integration configuration through `homeassistant.packages`.

## Recommended target structure

- [ ] Keep behavior packages organized by owner and feature.
  - [ ] `packages/areas/<area>/<feature>/<event>/<concern>.yaml`
  - [ ] `packages/people/<person>/<context>/<event>/<concern>.yaml`
  - [ ] `packages/reminders/<reminder>.yaml`
  - [ ] `packages/schedules/<schedule>.yaml`
  - [ ] `packages/shared/<feature>.yaml` for genuinely cross-area behavior.
- [ ] Put singleton Home Assistant root integrations at the package root for immediate discoverability.
  - [ ] Move `packages/integrations/influxdb.yaml` to `packages/influxdb.yaml`.
  - [ ] Move `packages/integrations/google_assistant.yaml` to `packages/google_assistant.yaml`.
  - [ ] Move `packages/integrations/device_tracker.yaml` to `packages/device_tracker.yaml` if the legacy LuCI YAML platform remains in use.
  - [ ] Move `packages/shared/logger.yaml` to `packages/logger.yaml`.
  - [ ] Move `packages/shared/recorder.yaml` to `packages/recorder.yaml`.
  - [ ] Treat `lovelace` similarly: consolidate dashboard registration and resources under `packages/lovelace/`, or use `packages/lovelace.yaml` if kept as one package.
  - [ ] Keep automation/helper packages associated with an integration under an owner directory only when their content is feature behavior rather than the integration’s singleton root configuration (for example, Adaptive Lighting schedules and reset automations can remain grouped).
- [ ] Make package names mirror their owner-relative path.
  - [x] Area package names already correctly omit the taxonomy container: `packages/areas/bedroom/presence/off/thermostat.yaml` uses `bedroom_presence_off_thermostat`.
  - [x] People, reminder, schedule, shared, and integration package names are unique and consistently snake_case.
  - [ ] After root moves, rename wrapper keys only when doing so cannot collide with a component key; document the exception for singleton root integrations.

## `packages/` findings

- [ ] Consolidate fragmented singleton configuration.
  - [ ] Google Assistant configuration is spread across `packages/integrations/google_assistant.yaml`, `packages/integrations/google_assistant/entity_config.yaml`, five area-level `google_assistant/entity_config.yaml` files, and `packages/areas/bedroom/climate/google_assistant.yaml`.
    - [ ] Keep the singleton credentials/settings at `packages/google_assistant.yaml`.
    - [ ] Keep area entity exposure near the area only if local ownership is more valuable than a single auditable exposure list; otherwise consolidate it under `packages/google_assistant/entity_config/`.
    - [ ] Move the hard-coded `secure_devices_pin` to `secrets.yaml` via `!secret`; it is credential-like configuration even if Home Assistant accepts the current literal.
  - [ ] Lovelace registration is split across `packages/shared/lovelace.yaml`, `packages/shared/lovelace/resources.yaml`, five files under `packages/shared/lovelace/dashboards/`, one bedroom package, and two storage-room printer packages.
    - [ ] Choose one owner for dashboard registration and use a predictable one-dashboard-per-file structure.
    - [ ] Keep area-specific dashboards near their area only if this exception is documented.
- [ ] Finish helper separation.
  - [x] The large shared helper sets (`background_music_input`, `presence_detection_input`, and `sqm_toggle_input`) follow the standalone helper-package convention.
  - [ ] Split helper definitions out of behavior files that still mix concerns, including:
    - [ ] `packages/areas/bedroom/morning.yaml`
    - [ ] `packages/areas/*/presence/gate/on.yaml` and `off.yaml`
    - [ ] `packages/areas/*/thermostat/presence/off.yaml` and `on.yaml`
    - [ ] `packages/areas/bathroom/light/restore.yaml`
    - [ ] `packages/areas/bathroom/contact/delays.yaml`
    - [ ] `packages/areas/*/light/transition/on.yaml` and `off.yaml`
    - [ ] `packages/schedules/sqm_toggle.yaml`
    - [ ] `packages/shared/vacuum/status.yaml`
  - [ ] Prefer feature-scoped `_input.yaml` packages where several input domains belong together; preserve existing entity IDs during moves.
- [ ] Remove naming that exposes implementation rather than intent.
  - [ ] Rename files such as `input_boolean.yaml`, `input_number/...`, and `input_select/...` to feature-oriented `_input.yaml` names.
  - [ ] Replace device-model names such as `kitchen_ld2410c` and `living_room_ld2410c_*` with semantic presence names only through a planned entity-ID migration; current naming makes hardware replacement unnecessarily invasive.
  - [ ] Standardize `homeassistant/` versus `home_assistant` spelling in paths and package names; Home Assistant’s component key remains `homeassistant`.
- [ ] Normalize automation syntax.
  - [x] The configuration is valid with both singular (`trigger`, `condition`, `action`) and plural (`triggers`, `conditions`, `actions`) forms.
  - [ ] Adopt one modern style across the repository. The audit found 286 legacy `- service:` actions and 131 `platform:` keys alongside modern `action:` and `trigger:` syntax.
  - [ ] Apply this as a mechanical migration in small batches, with a config check after each batch; avoid mixing schema modernization with behavior changes.
- [ ] Review automation overlap and ownership.
  - [ ] `packages/areas/living_room/presence/off/thermostat.yaml` and `packages/shared/presence/off/thermostat.yaml` can both turn off the same two climate entities from different presence signals.
    - [ ] Document the intended precedence and why both automations are needed, or consolidate the policy under one owner.
    - [ ] The shared off automation checks `input_boolean.living_room_presence_detection` rather than `input_boolean.common_presence_detection`; verify whether this is deliberate.
  - [ ] The equivalent “on” paths retain different timing and syntax (`shared` waits one minute while area behavior differs); make the asymmetry explicit.
  - [ ] Remove obsolete thermostat setpoint helper packages if the presence-off behavior now always uses `climate.turn_off`, or clearly document their remaining consumers.
- [ ] Reduce operational noise and obsolete compatibility configuration.
  - [ ] `packages/shared/logger.yaml` enables debug logging for `custom_components.vesync` and `pyvesync`; return these to warning/info when troubleshooting ends to reduce log volume and recorder/storage pressure.
  - [ ] Re-evaluate `packages/integrations/device_tracker.yaml`, which uses the legacy YAML LuCI platform, against the current integration setup before restructuring it.
  - [ ] Re-evaluate `packages/integrations/esphome_sensor_fixes.yaml` after ESPHome/device firmware upgrades; customization-based unit fixes can conceal an upstream entity-definition defect.
- [ ] Add structural CI checks.
  - [ ] Assert every package file has exactly one outer package key.
  - [ ] Assert package keys are unique and snake_case.
  - [ ] Assert explicit automation IDs and script/entity keys are unique.
  - [ ] Assert owner-relative package key/path agreement, with documented exceptions for root integrations.
  - [ ] Assert helper-only package policy and reject `initial:` on user-editable helpers.
  - [ ] Run Home Assistant `config check` in CI or in a pre-deployment workflow.

## `includes/` findings

- [ ] Remove or reconnect apparently legacy dashboard content.
  - [x] Eleven YAML dashboards are registered: Rooms, Devices, Overview, Configuration, default/hidden Dashboard, Presence, Tasks, Vacuum, Bedroom Display, and two printer dashboards.
  - [ ] Audit views not reachable from any registered dashboard entrypoint. Likely legacy candidates include directories such as `views/admin`, `battery`, `blinds`, `cast`, `cast_bedroom`, `climate`, `fans`, `home`, `lights`, `locks`, `media`, `network`, `remotes`, and `weather`.
    - [ ] Delete them if superseded.
    - [ ] Otherwise include them from an active dashboard; navigation alone does not load a view into a YAML dashboard.
  - [ ] Review `includes/lovelace/views/living_room/input_numbers.yaml`, which overlaps the newer room Configuration subview and unified Configuration dashboard.
- [ ] Make entrypoint naming uniform.
  - [x] The main role-based names (`dashboard_room.yaml`, `dashboard_device.yaml`, `dashboard_overview.yaml`, and `dashboard_vacuum.yaml`) follow the current convention.
  - [ ] Rename generic `default.yaml` to a role-based name such as `dashboard_default.yaml`.
  - [ ] Decide whether `configuration.yaml`, `presence.yaml`, and `tasks.yaml` are intentional documented exceptions or should use the same `dashboard_*.yaml` prefix.
  - [ ] Keep dashboard slugs stable when renaming files and update package registrations atomically.
- [ ] Reduce duplicate UI implementations.
  - [ ] Room pages use custom `default-view`, `generic-card`, `flex-card`, and `grid-card`, while Configuration views use native sections. Establish one layout contract per dashboard type and document required custom resources.
  - [ ] Prefer reusable area-card fragments consistently: bathroom, bedroom, kitchen, living room, and storage room already have primary-control and metric components, but other repeated configuration and navigation structures are hand-copied.
  - [ ] Consider generating repetitive room Configuration sections from a maintained entity manifest only if the generated YAML remains reviewable.
- [ ] Complete Rooms dashboard coverage.
  - [x] Bathroom, bedroom, kitchen, living room, and storage room each have an included Configuration subview and a matching navigation tile.
  - [ ] Apartment and hallway have helper sections in the unified Configuration dashboard but no room Configuration subview in `dashboard_room.yaml`; either add corresponding room views/subviews or document why they are excluded from Rooms.
  - [ ] Verify each Configuration tile remains the last item in its row after future card additions; the current compact files place it last in the visible card sequence.
- [ ] Maintain the unified Configuration dashboard invariant.
  - [x] All 112 YAML-defined `input_boolean`, `input_number`, `input_datetime`, `input_select`, and `input_text` helpers appear exactly once across `includes/lovelace/views/configuration/*.yaml`.
  - [x] No unified Configuration entity reference points to an undefined YAML helper.
  - [ ] Encode this exact-once comparison as an automated test so future helper additions cannot silently drift.
- [ ] Improve include hygiene.
  - [x] All inspected `!include` targets resolve, and the live config check reports no include errors.
  - [ ] Normalize trailing slashes on `!include_dir_named` paths.
  - [ ] Normalize line endings; the cast view files show CRLF artifacts while most of the tree uses LF.
  - [ ] Add a reachability checker starting from every filename registered under `lovelace.dashboards` and following `!include`/`!include_dir_named` recursively.
- [ ] Review dashboard access controls.
  - [ ] Several room views hard-code Home Assistant user UUIDs in `visible:` lists. Centralize/document these ACLs or remove them if dashboard registration already provides the intended access boundary.
  - [ ] Treat changes to those UUID lists as security-sensitive configuration and validate each user’s intended access.

## Migration checklist

- [ ] Phase 1: codify rules without behavior changes.
  - [ ] Decide the exact root integration wrapper convention described above.
  - [ ] Add package-shape, uniqueness, helper-dashboard coverage, include-resolution, and dashboard-reachability checks.
  - [ ] Record the chosen root integration exceptions in `AGENTS.md` and `.github/instructions/home-assistant.instructions.md`.
- [ ] Phase 2: move singleton integration packages.
  - [ ] Move one file at a time (`influxdb` first), retaining its valid outer wrapper and inner component key.
  - [ ] Update documentation/discoverability references.
  - [ ] Run `pnpm reload`, run a local Home Assistant config check, inspect core logs, and confirm the integration remains loaded after each move.
- [ ] Phase 3: separate remaining helpers.
  - [ ] Move definitions without renaming entity IDs.
  - [ ] Because these are existing entities, verify retained state after reload/restart; do not add `initial:` defaults.
  - [ ] Re-run the unified Configuration exact-once audit.
- [ ] Phase 4: Lovelace cleanup.
  - [ ] Produce a definitive reachable/orphan list.
  - [ ] Remove confirmed dead views or connect retained views to registered dashboards.
  - [ ] Reload and inspect dashboard errors; restart Core if old dashboard filenames remain cached.
- [ ] Phase 5: syntax modernization and behavior review.
  - [ ] Convert legacy YAML syntax mechanically.
  - [ ] Resolve duplicate thermostat policy ownership separately.
  - [ ] Validate automations in runtime logs after every bounded batch.

## Validation baseline

- [x] Home Assistant Core: 2026.8.1.
- [x] `pnpm home-assistant -H http://localhost:8123 config check`: valid, zero errors, zero warnings.
- [x] 352 package YAML files; 352 unique package wrapper keys.
- [x] No duplicate explicit automation IDs found.
- [x] 112 YAML-defined input helpers; 112 exact-once unified Configuration references.
- [x] No configuration files were moved or behavior changed as part of this audit.
