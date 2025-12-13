# Plan: Fix VeSync Entity Discovery

## Overview

The current implementation of the VeSync custom component incorrectly attempts to access device lists via `manager.devices.fans`. The `pyvesync` library exposes these lists directly on the manager instance as `manager.fans`. This plan corrects the attribute access in the fan and humidifier platforms to enable proper entity discovery.

## Steps

1.  **Update Fan Platform**
    - **Target**: `custom_components/vesync/fan.py`
    - **Action**: Change iteration from `manager.devices.fans` to `manager.fans`.
    - **Validation**: Verify code no longer references `manager.devices`.

2.  **Update Humidifier Platform**
    - **Target**: `custom_components/vesync/humidifier.py`
    - **Action**: Change iteration from `manager.devices.fans` to `manager.fans`.
    - **Validation**: Verify code no longer references `manager.devices`.

## Risks / Dependencies

- **Risk**: The `__init__.py` file contains `await manager.login()`. If `pyvesync` is synchronous, this will raise a TypeError. This plan focuses on entity creation, but that issue might block testing.
- **Risk**: If the installed version of `pyvesync` is non-standard, the structure might differ.
  - _Mitigation_: The standard library structure is well-known (`manager.fans`).

## Expectations for Implement / Review

- **Success**: After applying changes and restarting, VeSync fans and humidifiers should appear in Home Assistant.
- **Validation**: Check `plan_entity_creation.md` for detailed findings.
