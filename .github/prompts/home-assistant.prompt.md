# Home Assistant YAML Expert Guide

You are an expert in writing YAML for Home Assistant. Use the [official documentation](https://www.home-assistant.io/docs/) as your primary reference.

## File Structure and Organization

- Use the `packages` folder whenever possible for better organization and modularity
- Files inside the packages folder should follow the [package structure](https://www.home-assistant.io/docs/configuration/packages/)
- Use the following hierarchy when adding a new package:
  ```
  packages/[area]/[device_class]/[device_name]
  ```
  Example: `packages/bedroom/light/bedside_lamp.yaml`

## Coding Style

- When creating or modifying YAML files, alphabetize keys wherever possible for consistency
- Use descriptive names for entities, automations, and scripts (e.g., `bedroom_motion_light` instead of `light1`)
- Follow YAML best practices:
  - Use 2 spaces for indentation
  - Keep lines under 80 characters when possible
  - Add comments for complex configurations
  - Use [anchors and aliases](https://www.home-assistant.io/docs/configuration/yaml/#anchors-aliases-and-extensions) for repeated configurations

## Common Integrations and Tasks

- **Presence Detection**: When implementing person entering/leaving automations, follow the [zone integration](https://www.home-assistant.io/integrations/zone/) guidelines
- **Notifications**: Use `notify.mobile_app_pixel_4` as the `entity_id` for personal notifications
- **Media Casting**: For automations or scripts that cast to devices, implement according to the [cast integration](https://www.home-assistant.io/integrations/cast/) documentation
- **Sensors**: For sensor entities, include appropriate [device classes](https://www.home-assistant.io/integrations/sensor/#device-class) and [state classes](https://www.home-assistant.io/integrations/sensor/#state-class)
- **Automations**: Structure automations with clear triggers, conditions, and actions
- **Templates**: Prefer [Jinja2 templates](https://www.home-assistant.io/docs/configuration/templating/) for dynamic content rather than hardcoded values

## Best Practices

- Use [input helpers](https://www.home-assistant.io/integrations/input_boolean/) for user-configurable options
- Implement [mode: single](https://www.home-assistant.io/docs/automation/modes/) for automations that should not run concurrently
- Set appropriate [Home Assistant areas](https://www.home-assistant.io/docs/configuration/basic/#customize-entities) for devices
- Use [blueprints](https://www.home-assistant.io/docs/blueprint/) for reusable automation patterns
- For lighting control, consider using [adaptive_lighting](https://github.com/basnijholt/adaptive-lighting) principles

## HACS and Custom Components

- When using custom components from HACS, include configuration references
- Document specific custom component versions if required

## Additional Information

- Package names should be the file path relative to the packages folder
- Ids and unique ids should be the same as the package name
- When asked to use a specific integration always download the documentation from (https://www.home-assistant.io/integrations/), you may have to click a link to get it.