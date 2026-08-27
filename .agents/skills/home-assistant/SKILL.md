---
name: home-assistant
description: Maintain this repository's Home Assistant YAML packages, Lovelace dashboards, helpers, automations, scripts, and runtime configuration. Use for Home Assistant configuration changes, reviews, diagnosis, validation, or documentation in this workspace.
---

# Home Assistant Configuration

Apply the repository conventions below to Home Assistant work in this workspace. Preserve unrelated user changes and inspect nearby implementations before introducing a new pattern.

## Repository structure

- Keep all package YAML under `packages/areas/`, `packages/integrations/`, `packages/people/`, `packages/reminders/`, `packages/schedules/`, or `packages/shared/`. Never add package YAML directly under `packages/`.
- `homeassistant.packages` uses `!include_dir_merge_named packages/`; every YAML file below that directory is standalone loadable input. Do not create helper fragments in an active package directory unless each is a complete package entry.
- Prefix top-level package keys by taxonomy: `area_domain_feature`, `integrations_name`, `people_name_feature`, `reminders_name`, `schedules_name`, or `shared_domain_feature`.
- Use snake_case for package names, IDs, unique IDs, entity IDs, and related identifiers.
- When package or include discoverability changes, update the relevant documentation in the same change.

## YAML and automation conventions

- Omit default-valued keys, including `mode: single`, and omit empty conditions.
- Put comments before the block they describe, not at the end of a line or block.
- Separate automations that share a trigger but address different concerns. Prefer paths such as `tv/on/lights.yaml` and `tv/on/blinds.yaml` to a mixed `on.yaml`.
- Send mobile notifications through `notify.mobile_app_pixel_6_pro`.
- Use `flex-card` and `grid-card` for responsive layouts when custom responsive composition is required.

## Helpers and live settings

- Put `input_*` definitions in a standalone helper-only package rather than alongside automation, script, or integration logic. For a feature spanning input domains, use a feature-scoped `_input` package, such as `shared_background_music_input`.
- Back user-editable values with helpers instead of hard-coding them in runtime behavior.
- Do not use YAML `initial` for a migrated user-editable default. Preserve existing behavior with an explicit one-time post-reload seed, verify live state, and keep legacy defaults confined to that seed path.
- Make runtime scripts and automations fail closed when required helper state is blank or unavailable.
- Do not assume a reload changes an existing helper's live state. Verify it explicitly and use a service call or one-time migration when existing installations must adopt a value immediately.
- New helpers may require a Home Assistant core restart before their first seed or runtime check because reload does not always register new entities.
- For static configuration that cannot consume templates, apply helper-backed runtime settings from a script or automation on both startup and `automation_reloaded`, so reload reapplies them.

## Lovelace configuration views

- Put room configuration subviews at `includes/lovelace/views/<area>/configuration.yaml` and include them from `includes/lovelace/dashboards/dashboard_room.yaml`.
- Set `subview: true`; use `type: sections` or the sections default; place content under `sections:`, never a top-level `cards:` list.
- Group entities by concern. Use one built-in `entities` card per concern section, preserve entity order, omit the area name from labels, and surface only entities created or configured under `packages/`.
- Open each subview from a dedicated Configuration tile at `/dashboard-room/<area>-configuration`; keep that tile last on its row.
- Surface every YAML-defined `input_*` helper exactly once in `includes/lovelace/dashboards/configuration.yaml` and its detail views under `includes/lovelace/views/configuration/`. Group by shared concern or owning area/scope, while retaining room-specific configuration subviews.
- Dashboard entrypoint filenames use underscore role names, including `dashboard_overview.yaml`, `dashboard_device.yaml`, `dashboard_room.yaml`, `dashboard_vacuum.yaml`, `configuration.yaml`, `presence.yaml`, and `tasks.yaml`; dashboard slugs do not change with filenames.
- After renaming a dashboard entrypoint, inspect logs and restart core if the runtime still references the old path.

## Established feature patterns

- Presence-off climate behavior should fully turn thermostats off with `climate.turn_off` after a 15-second absence hold. Use `packages/areas/bedroom/presence/off/thermostat.yaml` as the reference. Bound Harmony `PowerToggle` debounce waits to 30 seconds as in `script.bedroom_air_conditioner_off`. Living-room and shared presence-off thermostat logic may still need migration from the older setpoint-only behavior.
- Expose the combined `climate.bedroom_thermostat` group to Google Assistant, not its separate heating and cooling implementation entities.
- For sunset blinds, use helper-backed positions. The living-room pattern disables `input_boolean.living_room_blinds_automatic`, then reads `input_number.living_room_blinds_sunset_position` when positioning `cover.living_room_blinds`. Prefer it to older hard-coded patterns.
- Bedroom sunset and TV-idle positioning intentionally share `input_number.bedroom_blinds_sunset_position`; its migration value was seeded once to 75.
- Background music uses Music Assistant library URIs such as `library://radio/2`, not opaque numeric media IDs. Target Music Assistant player entities, trim text-helper values when reading them, and gate scheduled play and stop actions with per-day enable helpers.

## Validation

After each meaningful configuration change:

1. Run `pnpm reload`.
2. Read runtime logs with `pnpm home-assistant raw request GET /api/hassio/core/logs --text`.
3. If the Supervisor endpoint is unavailable or returns an upstream error, use `pnpm home-assistant error-log`.
4. Confirm there are no warnings or errors caused by the change and verify relevant runtime entity state or behavior.

Use `pnpm home-assistant` for Home Assistant CLI operations; its documentation is in `bin/cli`, and it requires Node.js 22.6.0 or newer. From the Home Assistant host, add `-H http://localhost:8123` when the configured external URL is unavailable or slow. `ha core logs` and `ha core restart` are available for direct host administration when appropriate.

## Continuous improvement

Before completing every interaction in which this skill is used, perform a maintenance pass on this `SKILL.md`:

1. Identify any durable repository convention, verified runtime behavior, corrected assumption, or recurring failure mode learned during the interaction.
2. Update the most relevant existing rule; add a concise rule only when no existing rule covers the learning. Remove or consolidate stale guidance when evidence supersedes it.
3. Do not record transient state, task-specific narration, secrets, unverified guesses, or rules that merely restate general agent behavior.
4. Re-run the skill validator after an edit. If the interaction produced no durable learning, leave the file unchanged rather than manufacturing churn.

This maintenance pass is part of the task's definition of done. Mention material skill refinements in the final response.
