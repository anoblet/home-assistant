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

- Feature packages live under `packages/` and are grouped by area/domain/feature.
- Keep packages small and focused; prefer one responsibility per file.

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
