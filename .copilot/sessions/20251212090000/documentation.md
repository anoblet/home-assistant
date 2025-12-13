# VeSync Custom Component Documentation

## 1. Description

The `vesync` custom component integrates VeSync devices into Home Assistant. It allows users to control and monitor various VeSync smart home devices, including thermostats, air fryers, bulbs, outlets, humidifiers, and air purifiers. The component utilizes the `pyvesync` library to communicate with the VeSync API.

## 2. Supported Devices

The component supports a wide range of VeSync devices:

- **Thermostats**:
  - Control target temperature.
  - Set fan modes (Auto, Low, Medium, High).
  - Set HVAC modes (Off, Heat, Cool, Auto).
- **Air Fryers**:
  - **Sensors**:
    - Current Temperature
    - Cook Time Remaining
    - Kitchen Mode
- **Lights (Bulbs & Wall Dimmers)**:
  - **Dimmable Lights**: Control brightness.
  - **Tunable White Lights**: Control brightness and color temperature (2700K - 6500K).
  - **Color Lights (RGB)**: Control brightness, color temperature, and HS color.
- **Outlets**:
  - **Sensors**: Power (W), Energy (kWh), Voltage (V).
  - **History**: Weekly, Monthly, and Yearly energy usage.
- **Humidifiers**:
  - **Sensors**: Humidity (%), Temperature.
- **Air Purifiers**:
  - **Sensors**: Filter Life (%), Air Quality, PM2.5.

## 3. Installation

To install the `vesync` custom component:

1.  Copy the `vesync` directory to the `custom_components` folder in your Home Assistant configuration directory.
    - Path: `custom_components/vesync`
2.  Restart Home Assistant.

## 4. Configuration

The component uses a configuration flow, allowing setup directly from the Home Assistant UI.

1.  Go to **Settings** > **Devices & Services**.
2.  Click **Add Integration**.
3.  Search for **VeSync**.
4.  Enter your VeSync **Username** and **Password**.
5.  Click **Submit**.

_Note: Only a single instance of the integration is allowed._

## 5. Implementation Details

### Climate Platform

- **File**: `climate.py`
- **Class**: `VeSyncClimate`
- **Logic**: Maps VeSync modes (`auto`, `cool`, `heat`, `off`) to Home Assistant HVAC modes. Handles temperature conversion and fan mode mapping.

### Air Fryer Sensors

- **File**: `sensor.py`
- **Logic**: Sensors are dynamically added if the device type contains "airfryer".
- **Specific Sensors**:
  - `current_temperature`: Retrieves `current_temp` from device details.
  - `cook_time_remaining`: Retrieves `cook_time_remaining` from device details.
  - `kitchen_mode`: Retrieves `kitchen_mode` from device details.

### Lights

- **File**: `light.py`
- **Classes**: `VeSyncDimmableLightHA`, `VeSyncTunableWhiteLightHA`, `VeSyncColorLightHA`.
- **Logic**:
  - Converts Home Assistant brightness (0-255) to VeSync brightness (0-100).
  - Converts Home Assistant color temperature (Mireds) to VeSync color temperature (0-100 scale, inverted).
  - Handles HS color conversion for RGB bulbs.

## 6. Verification Results

- **Device Count**: 4
