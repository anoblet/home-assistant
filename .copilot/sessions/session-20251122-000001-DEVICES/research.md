# Research Report: Device Dashboard & Categories

## Findings

- **Lovelace Structure**:
  - `includes/lovelace/` contains `dashboards/` and `views/`.
  - `ui-lovelace.yaml` is a placeholder indicating dashboards are managed via packages.
  - `packages/lovelace.yaml` defines the active dashboards, specifically mapping `dashboard-devices` to `includes/lovelace/dashboards/dashboard-device.yaml`.
- **Device Dashboard**:
  - `includes/lovelace/dashboards/dashboard-device.yaml` exists and is the primary view for devices.
  - It contains views for: Summary, Lights, Climate & Air, Fans, Security & Presence, Batteries & Network.
  - `includes/lovelace/views/devices/` exists but is empty.
- **Device Categories**:
  - **Lights**: Zigbee light groups (`light.*_zigbee`), Adaptive Lighting integration.
  - **Climate**:
    - Thermostats & Heaters (ESPHome).
    - Air Conditioners (Midea, ESPHome).
    - Environmental Sensors (BME280, BME680, SCD30, SEN55 via ESPHome).
  - **Fans**: Air Purifiers (likely VeSync), generic fans.
  - **Security & Presence**:
    - Locks (`lock.back_door`).
    - Presence Sensors (LD2410c mmWave via ESPHome).
    - Motion Sensors & Door Contacts.
  - **Covers**: Blinds (ESPHome).
  - **Other**:
    - Vacuum (Valetudo referenced in `configuration.yaml`).
    - 3D Printer (Bambu Lab integration).
    - Cameras (WyzeAPI integration).

## Evidence

- `packages/lovelace.yaml`: Configures `dashboard-devices` pointing to `includes/lovelace/dashboards/dashboard-device.yaml`.
- `includes/lovelace/dashboards/dashboard-device.yaml`: Defines the layout and entities for the devices dashboard.
- `esphome/*.yaml`: Confirms existence of custom ESPHome devices for blinds, heaters, presence (LD2410c), and air quality.
- `custom_components/`: Indicates integrations for VeSync, Bambu Lab, Midea AC, Wyze, Spook.
- `configuration.yaml`: Shows CORS allowed origins for Valetudo (Vacuum).

## Gaps / Questions

- `includes/lovelace/views/devices/` is empty. Was it intended for sub-views that haven't been created yet?
- Specific entity IDs for some integrations (like Bambu Lab or Wyze) are not explicitly seen in the `dashboard-device.yaml` but are implied by the integrations.

## Planning Notes

- Any modifications to the Devices dashboard should be done in `includes/lovelace/dashboards/dashboard-device.yaml`.
- New device categories (like 3D Printers or Vacuums) could be added to the Devices dashboard as they are currently missing or not prominent.
- The `packages/lovelace.yaml` file is the central registry for dashboards; new dashboards must be added there.
