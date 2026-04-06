- [copilot-instructions](.github/copilot-instructions.md)
- [home-assistant](.github/instructions/home-assistant.instructions.md)

## Current Project Notes

- Treat `packages/areas/`, `packages/integrations/`, `packages/people/`, `packages/reminders/`, `packages/schedules/`, and `packages/shared/` as the active package taxonomy. All YAML package files reside exclusively under these six directories.
- Do not place new YAML files at the `packages/` root; all root-level packages have been migrated into taxonomy subdirectories.
- `homeassistant.packages` uses `!include_dir_merge_named packages/`, so every YAML file under `packages/` is loadable input. Do not place nested helper YAML fragments under active package owner folders unless each file is meant to be a standalone package entry.
- Top-level YAML keys follow taxonomy-prefixed snake_case: `area_domain_feature` for area packages, `integrations_name` for integration packages, `shared_domain_feature` for shared packages, `schedules_name` for schedule packages, `people_name_feature` for people packages, `reminders_name` for reminder packages.
- For area automations that react to one trigger across multiple concerns, prefer nested trigger directories with one concern per file, for example `packages/areas/living_room/tv/on/lights.yaml` and `packages/areas/living_room/tv/on/blinds.yaml`, instead of combining those actions in one `on.yaml` or `off.yaml` package.
- Lovelace dashboard entrypoint filenames under `includes/lovelace/dashboards/` are standardized by role, for example `overview.yaml`, `devices.yaml`, `rooms.yaml`, `areas.yaml`, and `vacuum.yaml`, while dashboard slugs remain unchanged.
- After moving or renaming Lovelace dashboard entrypoint files, `pnpm reload` may not fully refresh the running instance. Check logs and be prepared to restart Home Assistant if an old dashboard path is still referenced.
- Keep documentation updates in the same change when package or include discoverability changes.
- Update `.github/instructions/home-assistant.instructions.md` after each session to reflect any new learnings or adjustments to the above notes, ensuring that future sessions have the most accurate and up-to-date guidance.
