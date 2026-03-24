# Home Assistant

## Instructions

- After each meaningful change to the configuration, run `pnpm reload`, then check runtime logs via `pnpm home-assistant raw request GET /api/hassio/core/logs --text` (Supervisor) to confirm there are no warnings or errors related to the changes.
- `pnpm home-assistant` requires Node.js `>= 22.6.0` (see `bin/cli/README.md`).
- Do not use `mode: single` in automations since it is the default
- Do not use empty conditions
- Do not add erronenous keys where the value is the same as the default value
- Comments should be at the beginning of a code block, and not at the end.
- All package names, ids, unique_ids, entity_ids, etc. should use snake_case.
- Use the `notify.mobile_app_pixel_6_pro` service for all mobile notifications.

Use the `flex-card` and `grid-card` to create a responsive layout.

Avoid using `grep` in the root directory. Instead, use it within specific subdirectories to limit the scope of the search and improve performance.

Use the `pnpm home-assistant` command to run Home Assistant CLI commands. The documentation is located in the `bin/cli` directory.

## Commands

- Use `ha core logs` to view Home Assistant core logs.
- Use `ha core restart` to restart Home Assistant core.
