# Home Assistant

&& Instructions
- After every change, execute the following command in the terminal: `npx hass-cli call homeassistant reload_all`. Wait for the command to finish. An empty response is the sign of a successful reload. Check the `homeassistant.log` file for any new errors or warnings.
- Do not use `mode: single` in automations since it is the default
- Do not use empty conditions
- Comments should be at the beginning of a code block, and not at the end.
