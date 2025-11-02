# Home Assistant

## Instructions
- After each change run `pnpm reload` and review `home-assistant.log`. If there are any warnings or errors related to the changes that you've made, fix them.
- Do not use `mode: single` in automations since it is the default
- Do not use empty conditions
- Comments should be at the beginning of a code block, and not at the end.
- All package names, ids, unique_ids, entity_ids, etc. should use snake_case.
- Use the `notify.mobile_app_pixel_4_xl` service for all mobile notifications.
