"""Diagnostics support for VeSync."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pyvesync import VeSync

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry

from .common import get_base_unique_id
from .const import DOMAIN, VS_MANAGER

TO_REDACT: set[str] = {
    CONF_USERNAME,
    CONF_PASSWORD,
    "username",
    "email",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "uuid",
    "mac",
    "mac_id",
    "session",
    "headers",
}


def _coerce_value(value: Any) -> Any:
    """Coerce values into JSON-serializable structures."""

    if value is None or isinstance(value, (bool, int, float, str)):
        return value

    # Enums commonly expose a scalar `.value`.
    enum_value = getattr(value, "value", None)
    if enum_value is not None and isinstance(enum_value, (bool, int, float, str)):
        return enum_value

    if isinstance(value, dict):
        return {str(k): _coerce_value(v) for k, v in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [_coerce_value(v) for v in value]

    # Many pyvesync models use __slots__.
    slots = getattr(value, "__slots__", None)
    if isinstance(slots, Iterable):
        data: dict[str, Any] = {}
        for key in slots:
            if not isinstance(key, str) or key.startswith("_"):
                continue
            data[key] = _coerce_value(getattr(value, key, None))
        if data:
            return data

    # Fallback: string representation.
    return str(value)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    manager: VeSync = hass.data[DOMAIN][entry.entry_id][VS_MANAGER]

    devices = list(getattr(manager, "devices", []) or [])

    manager_devices = getattr(manager, "devices", None)
    summary: dict[str, Any] = {
        "timezone": getattr(manager, "time_zone", None),
        "total_device_count": len(devices),
    }

    # Include common container buckets when present.
    for attr in (
        "bulbs",
        "fans",
        "humidifiers",
        "air_purifiers",
        "outlets",
        "switches",
        "thermostats",
        "air_fryers",
    ):
        bucket = getattr(manager_devices, attr, None) if manager_devices is not None else None
        if bucket is not None:
            try:
                summary[f"{attr}_count"] = len(bucket)
            except TypeError:
                summary[f"{attr}_count"] = None

    data: dict[str, Any] = {
        "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        "manager": async_redact_data(_coerce_value(summary), TO_REDACT),
        "devices": [async_redact_data(_device_diagnostics_dict(d), TO_REDACT) for d in devices],
    }

    return data


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a device entry."""
    manager: VeSync = hass.data[DOMAIN][entry.entry_id][VS_MANAGER]

    vesync_device_id = next(
        (iden[1] for iden in device.identifiers if iden[0] == DOMAIN),
        None,
    )

    if vesync_device_id is None:
        return {
            "error": "VeSync identifier missing from Home Assistant device entry",
            "home_assistant": {
                "name": device.name,
                "name_by_user": device.name_by_user,
                "device_id": device.id,
                "identifier_domains": sorted({iden[0] for iden in device.identifiers}),
            },
            "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        }

    devices = list(getattr(manager, "devices", []) or [])
    vesync_device = next(
        (dev for dev in devices if get_base_unique_id(dev) == vesync_device_id),
        None,
    )

    if vesync_device is None:
        return {
            "error": "VeSync device not found in manager",
            "vesync_device_id": vesync_device_id,
            "entry_data": async_redact_data(dict(entry.data), TO_REDACT),
        }

    data: dict[str, Any] = async_redact_data(_device_diagnostics_dict(vesync_device), TO_REDACT)

    data["home_assistant"] = {
        "name": device.name,
        "name_by_user": device.name_by_user,
        "disabled": device.disabled,
        "disabled_by": device.disabled_by,
        "entities": [],
    }

    # Gather information how this VeSync device is represented in Home Assistant
    entity_registry = er.async_get(hass)
    hass_entities = er.async_entries_for_device(
        entity_registry,
        device_id=device.id,
        include_disabled_entities=True,
    )

    for entity_entry in hass_entities:
        state = hass.states.get(entity_entry.entity_id)
        state_dict = None
        if state:
            state_dict = dict(state.as_dict())
            # The context doesn't provide useful information in this case.
            state_dict.pop("context", None)

        cast(dict[str, Any], data["home_assistant"])["entities"].append(
            {
                "domain": entity_entry.domain,
                "entity_id": entity_entry.entity_id,
                "entity_category": entity_entry.entity_category,
                "device_class": entity_entry.device_class,
                "original_device_class": entity_entry.original_device_class,
                "name": entity_entry.name,
                "original_name": entity_entry.original_name,
                "icon": entity_entry.icon,
                "original_icon": entity_entry.original_icon,
                "unit_of_measurement": entity_entry.unit_of_measurement,
                "state": state_dict,
                "disabled": entity_entry.disabled,
                "disabled_by": entity_entry.disabled_by,
            }
        )

    return data


def _device_diagnostics_dict(device: Any) -> dict[str, Any]:
    """Build a curated, JSON-serializable diagnostics dict for a pyvesync device."""

    state = getattr(device, "state", None)
    state_dict: dict[str, Any] | None = None
    if state is not None:
        slots = getattr(state, "__slots__", None)
        if isinstance(slots, Iterable):
            state_dict = {
                key: _coerce_value(getattr(state, key, None))
                for key in slots
                if isinstance(key, str) and not key.startswith("_")
            }
        else:
            try:
                state_dict = {k: _coerce_value(v) for k, v in vars(state).items()}
            except TypeError:
                state_dict = {"repr": str(state)}

    return {
        "base_unique_id": get_base_unique_id(device),
        "device_name": getattr(device, "device_name", None),
        "device_type": getattr(device, "device_type", None),
        "device_class": device.__class__.__name__,
        "firmware": {
            "current": getattr(device, "current_firm_version", None),
            "latest": getattr(device, "latest_firm_version", None),
        },
        "connection_status": getattr(state, "connection_status", None) if state is not None else None,
        "device_status": getattr(state, "device_status", None) if state is not None else None,
        "state": state_dict,
    }
