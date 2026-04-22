# Home Assistant Configuration

![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Core-blue?style=for-the-badge&logo=home-assistant)
![ESPHome](https://img.shields.io/badge/ESPHome-Firmware-black?style=for-the-badge&logo=esphome)
![TypeScript](https://img.shields.io/badge/TypeScript-Strict-3178C6?style=for-the-badge&logo=typescript)
![Lit](https://img.shields.io/badge/Lit-Components-324FFF?style=for-the-badge&logo=lit)
![Node.js](https://img.shields.io/badge/Node.js-Tooling-339933?style=for-the-badge&logo=nodedotjs)

This repository contains a production Home Assistant configuration plus a local Copilot tooling workspace used for maintenance, analysis, and automation development.

## Repository Map

- `packages/`: Home Assistant packages grouped by area/domain/feature (for example `packages/areas/bedroom/`).
- `esphome/`: ESPHome firmware for room and device controllers.
- `custom_components/`: Third-party or custom integrations.
- `includes/lovelace/`: Dashboard view definitions, including the unified Configuration dashboard at `/dashboard-configuration`.
- `www/`: Frontend assets and custom web components.
- `copilot/`: Copilot-focused tooling and documentation.
- `docs/`: Internal architecture and operator documentation.
- `reports/`: Analysis snapshots.

## Documentation Index

- [`README.md`](README.md): Repository overview and operational quick start.
- [`docs/structure-guidelines.md`](docs/structure-guidelines.md): YAML style, package conventions, and validation workflow.
- [`docs/automations.md`](docs/automations.md): Automation architecture, patterns, and troubleshooting.
- [`docs/api/states.json`](docs/api/states.json): Sanitized sample of Home Assistant `GET /api/states` output.
- [`docs/custom-components/`](docs/custom-components): Integration-level notes for custom components.
- [`docs/api/`](docs/api): API-oriented documentation artifacts.
- [`reports/complexity.md`](reports/complexity.md): Historical complexity snapshot (not a live system map).
- [`copilot/README.md`](copilot/README.md): Copilot workspace overview and package links.

## Requirements

Use `pnpm` across the entire repository.

| Area                                                | Node.js             | Notes                                                 |
| --------------------------------------------------- | ------------------- | ----------------------------------------------------- |
| Root Home Assistant tooling (`pnpm home-assistant`) | `>= 22.6.0`         | See `bin/cli/README.md`                               |
| Copilot workspace packages (`copilot/packages/*`)   | `>= 24` recommended | `link` and `mcp` enforce Node 24 in package manifests |

## Quick Start

1. Install dependencies:

   ```bash
   pnpm install
   ```

2. Bootstrap workspace tooling:

   ```bash
   pnpm bootstrap
   ```

3. Configure local secrets (`secrets.yaml`, `.env`) as needed for your environment.

## Day-to-Day Commands

- Format files: `pnpm format`
- Run Home Assistant CLI: `pnpm home-assistant --help`
- Apply config reload: `pnpm reload`
- Restart Home Assistant core when brand-new `input_*` helpers do not appear after reload: `pnpm home-assistant core restart`
- Generate docs HTML preview: `pnpm docs:html`
- Open the unified helper dashboard: `/dashboard-configuration`

## Safety Notes

- Never commit raw runtime exports containing private network details or signed URLs.
- Keep `docs/api/states.json` as sanitized sample data only.
- Follow `.github/instructions/home-assistant.instructions.md` after meaningful configuration changes.

## Contributing Workflow

1. Keep changes focused and update documentation with code/config edits in the same pass.
2. Follow repository instructions in `.github/instructions/` and keep package names, IDs, and entity IDs in `snake_case`.
3. Run `pnpm reload` after meaningful Home Assistant changes.
4. If you added brand-new `input_*` helpers and they do not register after reload, restart Home Assistant core before first-time seeding and verification.
5. Verify runtime health with `pnpm home-assistant raw request GET /api/hassio/core/logs --text` and resolve warnings/errors before merge.
6. Confirm committed docs artifacts are sanitized (for example `docs/api/states.json`) and do not include private addresses, signed URLs, or secrets.
