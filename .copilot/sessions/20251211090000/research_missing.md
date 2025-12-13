# Research Report: Missing VeSync Devices

## Findings

- **Integration Path**: `custom_components/vesync`
- **Library Version**: `pyvesync==3.3.3` (defined in `manifest.json`)
- **Initialization**: `async_setup_entry` in `__init__.py` handles login and initial device fetch.
- **Update Mechanism**: `VeSyncDataCoordinator` in `coordinator.py` calls `manager.update()` every 60 seconds.

## Hypotheses

1.  **Shared Devices**: The missing devices might be shared from another VeSync account. `pyvesync` may treat shared devices differently or require specific handling that isn't fully active.
2.  **Home/Location**: If the user has multiple homes configured in the VeSync app, the API might only be returning devices from the default home.
3.  **Device Support**: The missing devices might be newer models not yet supported by `pyvesync` 3.3.3, or they might be categorized in a way the integration doesn't expect (e.g., `airfryer` or `thermostat` which are less common).
4.  **Outdated Library**: While 3.3.3 is a known version, there might be a newer version of `pyvesync` that addresses recent API changes or adds support for new devices.

## Debug Action

To diagnose exactly what `pyvesync` is seeing from the API, we should inject logging statements immediately after a successful login in `custom_components/vesync/__init__.py`.

**Suggested Edit for `custom_components/vesync/__init__.py`:**

Locate the `async_setup_entry` function and find the `if not login:` block. Add the debug logging immediately after it.

```python
    if not login:
        _LOGGER.error("Unable to login to VeSync")
        return False

    # --- DEBUG START ---
    _LOGGER.warning("VeSync Debug - Fans: %s", manager.fans)
    _LOGGER.warning("VeSync Debug - Bulbs: %s", manager.bulbs)
    _LOGGER.warning("VeSync Debug - Outlets: %s", manager.outlets)
    _LOGGER.warning("VeSync Debug - Switches: %s", manager.switches)
    # --- DEBUG END ---

    coordinator = VeSyncDataCoordinator(hass, manager)
```

After applying this change and restarting Home Assistant, check `home-assistant.log` for "VeSync Debug" entries to see the raw lists of devices returned by the library.
