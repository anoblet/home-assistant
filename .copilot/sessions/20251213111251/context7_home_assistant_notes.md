Context7 notes pulled from developers.home-assistant.io:

- Fan entity platform: derive from `homeassistant.components.fan.FanEntity`; supported features include speed/percentage, preset modes, oscillation, direction (if device supports it).
- Humidifier entity platform: derive from `homeassistant.components.humidifier.HumidifierEntity`; features include `HumidifierEntityFeature.MODES` and setting target humidity.
- Entity registry and naming:
  - Entities with `unique_id` are registered; unique_id must be stable and must not include domain/platform.
  - Entities should use `has_entity_name = True` for new integrations; entity `name` should not include device name.
  - Use entity descriptions (`EntityDescription` subclasses) with unique `key` values to help build stable `unique_id`s.
  - Avoid creating entities where the description key or translation_key is `None`; this can result in `*_none` entity ids.
