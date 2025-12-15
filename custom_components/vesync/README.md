# VeSync Custom Component

This is a custom component for Home Assistant to integrate with VeSync devices.

## Installation

1. Copy the `custom_components/vesync` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Add the integration via the UI.

## Configuration

Configuration is done via the UI.

## Recent Changes

### Dynamic Fan Modes Support
Fan modes are now dynamically retrieved from the device capabilities rather than being hardcoded. This ensures that only the modes supported by your specific device model are available in Home Assistant.

### Fix for Duplicate Entities (Unique ID Stability)
We have improved the generation of Unique IDs for entities to ensure stability across restarts and configuration changes. This fixes issues where entities might be duplicated or lose their history.

## Troubleshooting

### Duplicate Entities
If you notice duplicate entities after updating to this version, it is likely due to the change in how Unique IDs are generated. The old entities with the unstable IDs may still be present.

**Resolution:**
1. Navigate to **Settings** -> **Devices & Services** -> **Entities**.
2. Search for the duplicate entities (they might be marked as "Restored" or unavailable if the new ones have taken over, or you might see two active ones).
3. Select the old entities and delete them.
4. Restart Home Assistant to ensure everything is clean.

The new entities should persist correctly going forward.
