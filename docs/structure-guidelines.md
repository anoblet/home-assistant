# Structure & Style Guidelines

This repo treats Home Assistant configuration as code. These guidelines exist to keep YAML consistent, reviewable, and easy to diff.

## Documentation map

- Root onboarding: [`README.md`](../README.md)
- Automation reference: [`docs/automations.md`](automations.md)
- API sample artifact: [`docs/api/states.json`](api/states.json)
- Custom component docs: [`docs/custom-components/`](custom-components)
- Historical analysis snapshot: [`reports/complexity.md`](../reports/complexity.md)

## YAML conventions

- Use **two-space indentation**.
- Prefer **explicit, readable IDs** (automation IDs, script IDs, entity IDs) and keep them stable.
- Use `snake_case` for:
  - package names and paths
  - `id`, `unique_id`, `entity_id` fragments
  - helper/input names
- Avoid redundant defaults:
  - don’t set `mode: single` (it’s the default)
  - don’t add keys where the value equals the default
- Avoid empty or no-op blocks:
  - don’t add empty `condition:` lists
- Put comments **at the start of a block**, not trailing at the end of a line.

## Package layout

All package files live under `packages/` and are organized into six taxonomy directories:

| Directory       | Purpose                                                                                           | Files |
| --------------- | ------------------------------------------------------------------------------------------------- | ----- |
| `areas/`        | Area-scoped configuration (per-room devices, automations, scripts)                                | 242   |
| `integrations/` | Integration-specific configuration (adaptive_lighting, google_assistant, esphome, device_tracker) | 10    |
| `people/`       | Person-scoped configuration                                                                       | 6     |
| `reminders/`    | Reminder/notification packages                                                                    | 3     |
| `schedules/`    | Time-of-day schedule anchors (morning, evening, night, day)                                       | 4     |
| `shared/`       | Cross-cutting configuration (lovelace, presence, vacuum, zones, themes, media_player groups)      | 49    |

### Naming conventions

- **Directory and file names**: `snake_case` (no kebab-case).
- **Top-level YAML keys** (the package key used by `!include_dir_merge_named`):
  - Area packages: `{area}_{domain}_{feature}` — e.g., `bedroom_script_cast_display`
  - Integration packages: `integrations_{name}` — e.g., `integrations_adaptive_lighting`
  - Shared packages: `shared_{domain}_{feature}` — e.g., `shared_vacuum_start`
  - Schedule packages: `schedules_{name}` — e.g., `schedules_morning`
  - People packages: `people_{name}_{feature}`
  - Reminder packages: `reminders_{name}`
- All top-level keys must be **globally unique** across `packages/`.

### Placement rules

- Do **not** place new files at the `packages/` root level.
- Do **not** place new work outside the six taxonomy directories (`areas/`, `integrations/`, `people/`, `reminders/`, `schedules/`, `shared/`).
- Keep packages small and focused; prefer one responsibility per file.
- `homeassistant.packages` uses `!include_dir_merge_named packages/`, so every YAML file under `packages/` is loadable input. Do not place nested helper YAML fragments under active package owner folders unless each file is meant to be a standalone package entry.

### Area package structure

Each area directory follows a `{area}/{domain}/{feature}.yaml` hierarchy:

```
packages/areas/bedroom/
├── adaptive_lighting/
├── climate/
│   ├── carbon_dioxide/
│   └── ...
├── cover/
├── light/
├── presence/
├── script/
│   ├── air_conditioner/
│   ├── cast/
│   └── vacuum.yaml
└── ...
```

### Dashboard package conventions

- Dashboard registration packages use `filename:` paths pointing to `includes/lovelace/dashboards/...`. These paths are independent of the package file location and must not be changed when moving packages.
- Dashboard slugs (e.g., `bedroom-display`) are kebab-case by HA convention and must not be renamed.
- Dashboard entrypoint filenames in `includes/lovelace/dashboards/` remain kebab-case (renaming is deferred due to high risk).

### Room configuration subviews

- Room-specific Configuration views for the Rooms dashboard live at `includes/lovelace/views/<area>/configuration.yaml` with `subview: true` and `type: sections` or the default sections behavior.
- Declare room configuration content under a top-level `sections:` list and group tiles into concern-based section blocks. Use multiple sections when multiple concerns are surfaced, and allow a single named section when only one concern is present; the Bathroom configuration subview is the reference pattern for a multi-concern layout.
- Use built-in card types only, and give each surfaced configuration entity its own built-in `tile` card rather than grouping multiple entities into a single `entities` card.
- Keep labels area-free, include only entities created or configured by YAML packages under `packages/`, register each subview from `includes/lovelace/dashboards/dashboard_room.yaml`, and open it from a dedicated Configuration tile that stays last on its row in the area view.

## Validation workflow

- After meaningful changes, run `pnpm reload`, then check runtime logs via `pnpm home-assistant raw request GET /api/hassio/core/logs --text`.
- If you add or edit `shell_command:` entries, restart Home Assistant core before validating service availability; `pnpm reload` alone will not register new or changed shell-command services.
- `pnpm home-assistant` requires Node.js `>= 22.6.0` (see `bin/cli/README.md`).
- Follow the additional repo-specific instructions in [.github/instructions/home-assistant.instructions.md](../.github/instructions/home-assistant.instructions.md).

## Contributing workflow

1. Keep edits narrowly scoped and update docs in the same change when behavior or conventions change.
2. Run `pnpm reload` after meaningful Home Assistant edits.
3. Verify runtime logs with `pnpm home-assistant raw request GET /api/hassio/core/logs --text` and resolve warnings/errors before merge.
4. Validate that docs artifacts are sanitized and free of private addresses, signed URLs, and secrets.

## API sample redaction and generation guidance

`docs/api/states.json` is documentation data, not a live export. Keep it safe and reusable:

- Only commit sanitized sample entities.
- Replace private addresses, signed URLs, user identifiers, and environment-specific IDs with placeholders.
- Keep sample size intentionally small and representative.
- Validate JSON after editing.

When refreshing `docs/api/states.json`:

1. Capture raw API data to a temporary path outside the repository.
2. Copy only representative entities required for documentation into `docs/api/states.json`.
3. Redact or replace environment-specific values before commit (private IPs or hostnames, signed query parameters such as `authSig` and token-like values, and user identifiers or unique hardware identifiers).
4. Run the validation commands below and fix any findings.

Suggested checks before commit:

```bash
# Ensure no obvious private-network or signed-token leakage
grep -RInE "authSig=|192\.168\.|10\.[0-9]+\.[0-9]+\.[0-9]+|172\.(1[6-9]|2[0-9]|3[01])\." docs/api

# Ensure the sample JSON is parseable
node -e "import { readFileSync } from 'node:fs'; JSON.parse(readFileSync('/homeassistant/docs/api/states.json','utf8')); console.log('states.json valid');"
```

## Scripts

- Utility/verification scripts live under `scripts/` (for example, offline audits that read `.storage/`).
- Script output intended for in-repo storage must be safe/redacted (no tokens, passwords, or unredacted email-like identifiers).
- This repo uses an allowlist-style `.gitignore`; when adding new top-level folders, ensure they are explicitly included.
