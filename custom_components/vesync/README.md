# VeSync Custom Component

A custom component for VeSync devices, extending the official integration with support for Air Fryers and Thermostats.

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant.
2. Go to "Integrations".
3. Click the three dots in the top right corner and select "Custom repositories".
4. Add the URL of this repository and select "Integration" as the category.
5. Click "Add".
6. Find "VeSync" in the list and install it.
7. Restart Home Assistant.

### Manual Installation

1. Download the `vesync` folder from this repository.
2. Copy the `vesync` folder to your `custom_components` directory in your Home Assistant configuration.
3. Restart Home Assistant.

## Configuration

This integration supports configuration via the UI.

1. Go to Settings -> Devices & Services.
2. Click "+ ADD INTEGRATION".
3. Search for "VeSync" and select it.
4. Enter your VeSync username and password.
5. Follow the on-screen instructions to complete the setup.

## Supported Devices

This custom component supports all devices supported by the official integration, plus additional device types:

- Air Purifiers
- Humidifiers
- Outlets/Switches
- Bulbs
- **Air Fryers** (New)
- **Thermostats** (New)

## Credits

This component is based on the official Home Assistant VeSync integration and uses the [pyvesync](https://github.com/webdjoe/pyvesync) library.
