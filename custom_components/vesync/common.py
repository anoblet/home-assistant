"""Common utilities for VeSync Component."""

from __future__ import annotations

import logging
from typing import Any

from pyvesync.base_devices import VeSyncHumidifier
from pyvesync.base_devices.fan_base import VeSyncFanBase
from pyvesync.base_devices.fryer_base import VeSyncFryer
from pyvesync.base_devices.outlet_base import VeSyncOutlet
from pyvesync.base_devices.purifier_base import VeSyncPurifier
from pyvesync.base_devices.thermostat_base import VeSyncThermostat
from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice
from pyvesync.devices.vesyncswitch import VeSyncWallSwitch

_LOGGER = logging.getLogger(__name__)


def get_base_unique_id(device: Any) -> str:
    """Return a stable unique id for a pyvesync device.

    The integration historically used `cid` and optional `sub_device_no` (for
    multi-channel devices) without a delimiter to avoid entity/device churn.
    """

    cid = getattr(device, "cid", None)
    if cid is None:
        return ""

    sub_device_no = getattr(device, "sub_device_no", None)
    if sub_device_no is not None:
        return f"{cid}{sub_device_no!s}"

    return str(cid)


def iter_manager_devices(manager: Any) -> list[Any]:
    """Return all devices known to a pyvesync manager (deduped).

    pyvesync==3.3.3 exposes devices via `manager.devices` (DeviceContainer).
    Some categories are also available as container properties.
    """

    devices: list[Any] = []
    seen: set[str] = set()

    def _add(dev: Any) -> None:
        uid = get_base_unique_id(dev)
        if not uid or uid in seen:
            return
        seen.add(uid)
        devices.append(dev)

    container = getattr(manager, "devices", None)
    if container is None:
        return devices

    for dev in list(container) or []:
        _add(dev)

    # Include explicit DeviceContainer buckets (if present) for completeness.
    for attr in ("air_fryers", "thermostats"):
        bucket = getattr(container, attr, None)
        for dev in bucket or []:
            _add(dev)

    return devices


def rgetattr(obj: object, attr: str):
    """Return a string in the form word.1.2.3 and return the item as 3. Note that this last value could be in a dict as well."""
    _this_func = rgetattr
    sp = attr.split(".", 1)
    if len(sp) == 1:
        left, right = sp[0], ""
    else:
        left, right = sp

    if isinstance(obj, dict):
        obj = obj.get(left)
    elif hasattr(obj, left):
        obj = getattr(obj, left)
    else:
        return None

    if right:
        obj = _this_func(obj, right)

    return obj


def is_humidifier(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents a humidifier."""

    return isinstance(device, VeSyncHumidifier)


def is_fan(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents a fan."""

    return isinstance(device, VeSyncFanBase)


def is_outlet(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents an outlet."""

    return isinstance(device, VeSyncOutlet)


def is_wall_switch(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents a wall switch, note this doessn't include dimming switches."""

    return isinstance(device, VeSyncWallSwitch)


def is_purifier(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents an air purifier."""

    return isinstance(device, VeSyncPurifier)


def is_thermostat(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents a thermostat."""

    return isinstance(device, VeSyncThermostat)


def is_fryer(device: VeSyncBaseDevice) -> bool:
    """Check if the device represents a kitchen device (air fryer)."""

    return isinstance(device, VeSyncFryer)
