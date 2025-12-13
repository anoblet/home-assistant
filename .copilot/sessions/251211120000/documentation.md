# VeSync Custom Component Documentation

## Summary

This session focused on creating a custom Home Assistant component for VeSync devices, specifically to add support for devices not currently supported by the official integration, such as Air Fryers and Thermostats.

## Steps Taken

1.  **Research**: Analyzed the official `vesync` integration and the `pyvesync` library. Identified that `pyvesync` supports Air Fryers and Thermostats, but the official HA integration does not.
2.  **Plan**: Designed a custom component structure based on the official integration. Planned the addition of `climate.py` for thermostats and `button.py` for air fryers, along with updates to `sensor.py`, `binary_sensor.py`, and `common.py`.
3.  **Implementation**: Created the full component structure in `/homeassistant/custom_components/vesync`. Implemented the new platforms and updated existing ones to support the new device types.
4.  **Review**: Verified that all files were created correctly and that the code implements the planned features. Confirmed the manifest requirements.

## Component Details

- **Path**: `/homeassistant/custom_components/vesync`
- **Domain**: `vesync`
- **Library**: `pyvesync==3.3.3` (Latest version)

## Features

- **Full Official Support**: Retains support for Outlets, Switches, Fans, Purifiers, Humidifiers, and Bulbs.
- **Air Fryers**:
  - **Sensors**: Temperature, Cook Time, Remaining Time, Status, Recipe Name.
  - **Binary Sensors**: Is Cooking, Is Heating.
  - **Button**: Stop Cooking.
- **Thermostats**:
  - **Climate Entity**: Supports Heat, Cool, Auto, Off modes.
  - **Controls**: Target Temperature, Fan Mode.

## Installation & Usage

1.  Restart Home Assistant.
2.  Go to **Settings > Devices & Services**.
3.  Add Integration and search for "VeSync".
4.  Login with your VeSync credentials.
