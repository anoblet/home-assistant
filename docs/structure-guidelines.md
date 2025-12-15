# Structure & Style Guidelines

This repo treats Home Assistant configuration as code. These guidelines exist to keep YAML consistent, reviewable, and easy to diff.

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
- Follow the additional repo-specific instructions in [.github/instructions/home-assistant.instructions.md](../.github/instructions/home-assistant.instructions.md).

## Scripts

- Utility/verification scripts live under `scripts/` (for example, offline audits that read `.storage/`).
- Script output intended for in-repo storage must be safe/redacted (no tokens, passwords, or unredacted email-like identifiers).
- This repo uses an allowlist-style `.gitignore`; when adding new top-level folders, ensure they are explicitly included.
