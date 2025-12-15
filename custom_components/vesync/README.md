# VeSync Custom Component

This is a custom component for Home Assistant to integrate with VeSync devices. It replaces the built-in VeSync integration with additional features, bug fixes, and support for a wider range of devices.

## Features

### 🚀 New Architecture: Split Coordinators

To ensure optimal performance and responsiveness while respecting API rate limits, this component now uses a split coordinator architecture:

- **State Coordinator**: Updates device states (power, mode, fan speed, etc.) frequently (every 60 seconds). This ensures that your dashboard reflects the actual state of your devices with minimal delay.
- **Energy Coordinator**: Updates energy monitoring data (voltage, power usage, etc.) less frequently (every 6 hours). Since energy data does not change as rapidly as device state, this reduces unnecessary API calls and improves overall stability.

### 🛠️ Device Fixes

- **LUH-A602S-WUS Humidifier**: Includes a specific patch to handle "Error processing bypass V2 API response result" errors. This ensures that the humidifier operates correctly without flooding the logs with API errors.

### ✨ Key Features

- **Extended Device Support**: Supports newer VeSync devices including humidifiers, air fryers, and air purifiers that may not be fully supported by the official integration.
- **Enhanced Entities**: Provides detailed sensors and configuration options such as night light, auto preference, and more.
- **Dynamic Fan Modes**: Fan modes are dynamically retrieved from device capabilities.
- **Parallel Updates**: Improved performance with parallel energy monitoring updates.
- **Localization**: Full support for Home Assistant translation keys.

## Supported Platforms

This integration supports the following platforms:

- **Binary Sensor**: Door open/closed status, tank status, etc.
- **Button**: Reset filter, etc.
- **Climate**: Thermostat control.
- **Fan**: Air purifiers and fans.
- **Humidifier**: Humidifier control with various modes.
- **Light**: Night lights and display lights.
- **Number**: Mist levels, fan speeds, etc.
- **Select**: Mode selection, preset selection.
- **Sensor**: Air quality, humidity, temperature, energy usage, filter life.
- **Switch**: Power control, child lock, etc.
- **Update**: Firmware update availability.

## Installation

1. Copy the `custom_components/vesync` folder to your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Go to **Settings** -> **Devices & Services**.
4. Click **Add Integration** and search for "VeSync".
5. Enter your VeSync credentials.

## Configuration

Configuration is handled entirely via the User Interface.

## Services

The integration provides the following custom services:

### `vesync.update_devices`

Discover newly added VeSync devices and add them to Home Assistant without restarting.

### `vesync.fryer_cook`

Start cooking on a supported VeSync air fryer.

- **temperature**: Cooking temperature.
- **time**: Cooking time in minutes.

### `vesync.fryer_set_preheat`

Set preheat on a supported VeSync air fryer.

- **temperature**: Preheat temperature.
- **cook_time**: Cook time in minutes (after preheat).

## Migration of Legacy Entities

This component includes automatic migration logic to fix issues with legacy entities:

- **Unique ID Stability**: Older versions of the integration may have generated unstable unique IDs. The component automatically migrates these to stable IDs.
- **Entity Naming**: Entities that were previously created with generic names (ending in `_none`) are automatically renamed to more descriptive names (e.g., `_power`, `_humidity`).
- **Cleanup**: If a legacy entity cannot be renamed (e.g., because the target name is already taken), the legacy entity is removed so it can be recreated correctly.

## Troubleshooting

### Duplicate Entities

If you notice duplicate entities after updating, it may be due to the migration of Unique IDs.

**Resolution:**

1. Navigate to **Settings** -> **Devices & Services** -> **Entities**.
2. Search for the duplicate entities.
3. Delete the old/unavailable entities.
4. Restart Home Assistant.
