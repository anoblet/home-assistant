# Home Assistant Configuration

This repository captures the full Home Assistant setup that powers Andrew Noblet's apartment. It brings together automation packages, custom integrations, Lovelace dashboards, ESPHome device builds, and supporting tooling so the entire smart home can be reproduced, audited, or iterated in source control.

## What You Will Find Here

- Package-driven Home Assistant configuration organised by area, domain, and feature under `packages/`, with IDs that mirror the folder hierarchy for traceability.
- A large automation catalog (144+ flows) covering presence, lighting, climate, media, appliance control, and safety scenarios, documented in `automation-flowchart.md`.
- Lovelace dashboards, views, and supporting assets stored under `includes/lovelace/` with per-view directories to keep UI definitions modular.
- Custom integrations and overrides in `custom_components/` (such as `adaptive_lighting`, `bambu_lab`, `vesync`, `wyzeapi`, and the in-house `spook` utilities) alongside templating helpers in `custom_templates/`.
- ESPHome firmware definitions for room sensors, cover controllers, air-quality monitors, and utility devices inside `esphome/` so hardware deployments stay in sync with Home Assistant expectations.
- Tooling to lint, format, document, and bootstrap the configuration via `package.json`, `copilot/`, and the bespoke `hass-cli` commands referenced throughout the instructions.

## Configuration Architecture

- `configuration.yaml` enables `packages: !include_dir_merge_named packages/`, making each package responsible for a small, well-scoped feature set (e.g., `packages/bedroom/light/...`, `packages/living_room/climate/...`).
- Shared helpers, notifications, and global behaviours live in `packages/common/` and `packages/homeassistant/`, while dashboard registration is handled in `packages/lovelace/`.
- Automation metadata, entity naming, and YAML style follow the guidelines in `.github/instructions/` and the [`docs/structure-guidelines.md`](./docs/structure-guidelines.md) reference to ensure consistency (two-space indentation, single quotes, ordered keys, descriptive IDs, `snake_case` paths).
- Secrets, environment-specific values, and integration credentials are kept out of version control via `secrets.yaml` references and `.gitignore` rules.

## Automation Pillars

- **Presence-driven logic** integrates device trackers, LD2410C radar sensors, and PIR motion across rooms to govern lighting, HVAC, and media states when occupants arrive, move, or leave.
- **Time and sun scheduling** ties adaptive lighting, sleep transitions, and morning routines to sunrise, sunset, weekday/weekend windows, and user-defined timers.
- **Environment management** monitors particulate matter, CO2, humidity, and temperature sensors to drive humidifiers, air purifiers, fans, and climate group set-points.
- **Cover and light coordination** keeps blinds aligned with daylight and privacy needs, while adaptive lighting maintains colour temperature and brightness profiles.
- **Security and safety responses** surface water leaks, door contact changes, and away-mode triggers through targeted notifications and automation resets.
- **Appliance orchestration** handles vacuum scheduling, background music playback, printer consumable tracking, and other utility tasks.

## Dashboards and User Experience

- Primary dashboards, including area-focused and task-oriented views, are assembled in `includes/lovelace/dashboards/` and `includes/lovelace/views/`.
- Legacy `ui-lovelace.yaml` is retained for reference, while active views are modularised for reuse across dashboards.
- The UI leans on Mushroom cards, adaptive lighting controls, media shortcuts, and status panels aligned with the Home Assistant style guidance captured in `packages/frontend/`.

## Custom and Third-Party Integrations

- The repository bundles several custom components under `custom_components/`, covering device-specific APIs (Bambu Lab printers, VeSync switches, Wyze sensors) and utility layers (`browser_mod`, `climate_group`, `spook_inverse`).
- Notes for the in-repo VeSync integration (services, logging, feature coverage, and device-targeted controls for thermostats/air fryers) live in [`docs/custom-components/vesync.md`](./docs/custom-components/vesync.md) along with the version-pinned mapping in [`docs/custom-components/vesync-pyvesync-coverage.md`](./docs/custom-components/vesync-pyvesync-coverage.md).
- HACS-managed resources live under `www/` and are referenced from Lovelace packages to extend the frontend with custom cards.
- MQTT, InfluxDB, Google Assistant, and other platform integrations are configured through dedicated package files and secret references.

## ESPHome Fleet

- Each ESPHome YAML file in `esphome/` targets a specific room or device, pairing sensors (BME280, SCD30, SEN55, LD2410C) with Wi-Fi boards (ESP32, ESP8266, ESP32-S3) and aligning entity names with Home Assistant packages.
- Shared packages under `esphome/packages/` standardise logging, sensor calibration, and entity metadata to keep deployments consistent.

## Tooling and Workflow

- `npm run bootstrap` (via `tsx copilot/bootstrap/index.ts`) prepares local tooling, Git hooks, and auxiliary scripts.
- Formatting relies on Prettier (`npm run format`), while `lint-staged` enforces clean YAML, JSON, and JS commits.
- The custom `hass-cli` (GitHub: `anoblet/hass-cli`) provides commands for state inspection, automation validation, and reload routines, with expectations documented in `.github/instructions/home-assistant.instructions.md`.
- Wireit tasks (`npm run git:commit`, `npm run git:push`) orchestrate commit and push workflows, optionally generating AI-assisted commit messages via GenAIScript.

## Getting Started

1. Install Home Assistant Core or Supervised on a host with access to the devices defined in this repository.
2. Clone the repository into your Home Assistant configuration directory (`/config` or equivalent) and ensure `secrets.yaml` contains the required credentials (InfluxDB, external URLs, API keys).
3. Install Node.js 20+ and run `npm install` to set up tooling, then execute `npm run bootstrap` to provision local hooks.
4. Review the instructions under `.github/instructions/` and `TASKS.md` to understand naming conventions, pending refactors, and required validation steps.
5. Use Home Assistant's configuration validation, `hass-cli`, or `yamllint` before reloading the configuration; after reloads, inspect `home-assistant.log` for regressions.
6. Build and flash ESPHome devices from the `esphome/` directory to keep sensor firmware aligned with the expected entities.

## Roadmap and Housekeeping

- Active refactors and clean-up tasks are tracked in `TASKS.md`, covering package hierarchy normalisation, Lovelace consolidation, YAML style enforcement, and automation metadata improvements.
- Pull requests should reference the applicable task checklist, include validation notes, and follow the style requirements documented in `.github/instructions/`.

For inspiration, troubleshooting tips, and official platform guidance, consult the [Home Assistant documentation](https://www.home-assistant.io/docs/). Keeping configuration as code in this repository ensures every change is reviewable, testable, and reproducible across the smart home estate.

## Todo

- [ ] Custom VeSync component: validate latest fan/humidifier fixes via `ha core restart` + `ha core logs`
