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
- After meaningful changes, run `pnpm reload`, then check runtime logs via `ha core logs`.
- Follow the additional repo-specific instructions in [.github/instructions/home-assistant.instructions.md](../.github/instructions/home-assistant.instructions.md).
