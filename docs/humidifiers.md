# Virtual humidifier targets

Bedroom and living-room virtual humidifiers use the room humidity sensors to control the physical humidifiers. Presence automations still control whether each virtual controller is on.

Each room owns three standalone packages under `packages/areas/<room>/humidifier/`: `virtual.yaml` defines the generic hygrostat and its stable unique ID, `input.yaml` defines the persistent target humidity helper, and `target.yaml` synchronizes that helper with the controller.

The target helpers appear in both the unified Configuration dashboard and the room Configuration subviews. Editing either the helper or the virtual humidifier target updates the other. Startup, automation reload and controller recovery reapply the helper target; entity creation and recovery do not overwrite the helper with a fallback target. No YAML initial value resets the user's setting.

This avoids relying solely on generic hygrostat restore data: startup logs on November 9 and 10, 2026 showed both controllers reporting `No previously saved humidity, setting to 0`. Their existing live targets were 50% when the persistent helpers were introduced.
