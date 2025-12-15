"""Service handlers for the VeSync integration.

These services expose pyvesync controls that don't map cleanly to standard HA
entity models (or would create excessive entity churn).
"""

from __future__ import annotations

from collections.abc import Iterator
import logging
from typing import Any

import voluptuous as vol

from pyvesync import VeSync
from pyvesync.base_devices.fryer_base import VeSyncFryer
from pyvesync.base_devices.thermostat_base import VeSyncThermostat
from pyvesync.const import ThermostatEcoTypes

from homeassistant.const import ATTR_DEVICE_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import device_registry as dr

from .common import get_base_unique_id, is_fryer, is_thermostat, iter_manager_devices
from .const import (
    DOMAIN,
    SERVICE_FRYER_COOK,
    SERVICE_FRYER_COOK_FROM_PREHEAT,
    SERVICE_FRYER_SET_PREHEAT,
    SERVICE_THERMOSTAT_CANCEL_HOLD,
    SERVICE_THERMOSTAT_SET_ECO_TYPE,
    SERVICE_THERMOSTAT_SET_LOCK,
    VS_COORDINATOR,
    VS_MANAGER,
)

_LOGGER = logging.getLogger(__name__)


_ECO_TYPE_MAP: dict[str, ThermostatEcoTypes] = {
    "comfort_second": ThermostatEcoTypes.COMFORT_SECOND,
    "comfort_first": ThermostatEcoTypes.COMFORT_FIRST,
    "balance": ThermostatEcoTypes.BALANCE,
    "eco_first": ThermostatEcoTypes.ECO_FIRST,
    "eco_second": ThermostatEcoTypes.ECO_SECOND,
}
def _iter_all_manager_devices(manager: VeSync) -> Iterator[Any]:
    """Yield devices across all pyvesync manager buckets (deduped)."""

    yield from iter_manager_devices(manager)


def _get_entry_and_device(
    hass: HomeAssistant,
    device_id: str,
) -> tuple[str, VeSync, Any]:
    device_registry = dr.async_get(hass)
    device_entry = device_registry.async_get(device_id)
    if device_entry is None:
        raise HomeAssistantError(f"Unknown device_id: {device_id}")

    base_unique_ids = [
        identifier[1] for identifier in device_entry.identifiers if identifier[0] == DOMAIN
    ]
    if not base_unique_ids:
        raise HomeAssistantError(
            "Device is not a VeSync device (missing vesync identifiers)"
        )
    base_unique_id = base_unique_ids[0]

    domain_entries = hass.data.get(DOMAIN, {})
    entry_ids = [
        entry_id
        for entry_id in device_entry.config_entries
        if entry_id in domain_entries
    ]
    if not entry_ids:
        raise HomeAssistantError(
            "Device is not associated with an active VeSync config entry"
        )

    entry_id = entry_ids[0]
    manager: VeSync = hass.data[DOMAIN][entry_id][VS_MANAGER]

    vesync_device = next(
        (
            dev
            for dev in _iter_all_manager_devices(manager)
            if get_base_unique_id(dev) == base_unique_id
        ),
        None,
    )
    if vesync_device is None:
        raise HomeAssistantError(
            "VeSync device was not found in the manager; try running vesync.update_devices"
        )

    return entry_id, manager, vesync_device


def _extract_device_ids(call: ServiceCall) -> list[str]:
    target = getattr(call, "target", None)
    target_device_ids = getattr(target, "device_ids", None)
    if target_device_ids:
        return list(target_device_ids)

    raw = call.data.get(ATTR_DEVICE_ID) or call.data.get("device_id")
    if raw is None:
        raise HomeAssistantError("Missing device target (device_id)")
    if isinstance(raw, str):
        return [raw]
    return list(raw)


_SCHEMA_DEVICE_TARGET = vol.Schema(
    {
        vol.Optional(ATTR_DEVICE_ID): vol.All(cv.ensure_list, [cv.string]),
    }
)

_SCHEMA_FRYER_COOK = _SCHEMA_DEVICE_TARGET.extend(
    {
        vol.Required("temperature"): vol.Coerce(int),
        vol.Required("time"): vol.Coerce(int),
    }
)

_SCHEMA_FRYER_SET_PREHEAT = _SCHEMA_DEVICE_TARGET.extend(
    {
        vol.Required("temperature"): vol.Coerce(int),
        vol.Required("cook_time"): vol.Coerce(int),
    }
)

_SCHEMA_THERMOSTAT_SET_LOCK = _SCHEMA_DEVICE_TARGET.extend(
    {
        vol.Required("locked"): cv.boolean,
        vol.Optional("pin"): vol.Any(cv.string, vol.Coerce(int)),
    }
)

_SCHEMA_THERMOSTAT_SET_ECO = _SCHEMA_DEVICE_TARGET.extend(
    {
        vol.Required("eco_type"): vol.Any(vol.Coerce(int), vol.Lower),
    }
)


def async_register_services(hass: HomeAssistant) -> None:
    """Register VeSync services (idempotent)."""

    async def _async_fryer_cook(call: ServiceCall) -> None:
        data = _SCHEMA_FRYER_COOK(call.data)
        temperature = int(data["temperature"])
        cook_time = int(data["time"])

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_fryer(device) or not isinstance(device, VeSyncFryer) or not hasattr(
                device, "cook"
            ):
                raise HomeAssistantError("Target device does not support fryer cook")

            if not await device.cook(temperature, cook_time):
                raise HomeAssistantError(getattr(device.last_response, "message", "Cook failed"))

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    async def _async_fryer_set_preheat(call: ServiceCall) -> None:
        data = _SCHEMA_FRYER_SET_PREHEAT(call.data)
        temperature = int(data["temperature"])
        cook_time = int(data["cook_time"])

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_fryer(device) or not isinstance(device, VeSyncFryer) or not hasattr(
                device, "set_preheat"
            ):
                raise HomeAssistantError("Target device does not support fryer preheat")

            if not await device.set_preheat(temperature, cook_time):
                raise HomeAssistantError(
                    getattr(device.last_response, "message", "Preheat failed")
                )

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    async def _async_fryer_cook_from_preheat(call: ServiceCall) -> None:
        _SCHEMA_DEVICE_TARGET(call.data)

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_fryer(device) or not isinstance(device, VeSyncFryer) or not hasattr(
                device, "cook_from_preheat"
            ):
                raise HomeAssistantError(
                    "Target device does not support cook_from_preheat"
                )

            if not await device.cook_from_preheat():
                raise HomeAssistantError(
                    getattr(device.last_response, "message", "Cook from preheat failed")
                )

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    async def _async_thermostat_cancel_hold(call: ServiceCall) -> None:
        _SCHEMA_DEVICE_TARGET(call.data)

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_thermostat(device) or not isinstance(device, VeSyncThermostat) or not hasattr(
                device, "cancel_hold"
            ):
                raise HomeAssistantError("Target device does not support cancel_hold")

            if not await device.cancel_hold():
                raise HomeAssistantError(
                    getattr(device.last_response, "message", "Cancel hold failed")
                )

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    async def _async_thermostat_set_lock(call: ServiceCall) -> None:
        data = _SCHEMA_THERMOSTAT_SET_LOCK(call.data)
        locked: bool = data["locked"]
        pin = data.get("pin")

        if locked and pin is None:
            raise HomeAssistantError("pin is required when locked is true")

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_thermostat(device) or not isinstance(device, VeSyncThermostat) or not hasattr(
                device, "toggle_lock"
            ):
                raise HomeAssistantError("Target device does not support lock")

            if not await device.toggle_lock(locked, pin=pin):
                raise HomeAssistantError(
                    getattr(device.last_response, "message", "Set lock failed")
                )

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    async def _async_thermostat_set_eco_type(call: ServiceCall) -> None:
        data = _SCHEMA_THERMOSTAT_SET_ECO(call.data)
        eco_raw = data["eco_type"]

        eco_type: ThermostatEcoTypes | None = None
        if isinstance(eco_raw, int):
            try:
                eco_type = ThermostatEcoTypes(eco_raw)
            except Exception:  # noqa: BLE001
                eco_type = None
        elif isinstance(eco_raw, str):
            eco_type = _ECO_TYPE_MAP.get(eco_raw.strip().lower())
            if eco_type is None:
                try:
                    eco_type = ThermostatEcoTypes(int(eco_raw))
                except Exception:  # noqa: BLE001
                    eco_type = None

        if eco_type is None:
            raise HomeAssistantError(
                "Invalid eco_type; use one of comfort_second/comfort_first/balance/eco_first/eco_second"
            )

        for device_id in _extract_device_ids(call):
            entry_id, _manager, device = _get_entry_and_device(hass, device_id)
            if not is_thermostat(device) or not isinstance(device, VeSyncThermostat) or not hasattr(
                device, "set_eco_type"
            ):
                raise HomeAssistantError("Target device does not support eco type")

            if not await device.set_eco_type(eco_type):
                raise HomeAssistantError(
                    getattr(device.last_response, "message", "Set eco type failed")
                )

            await hass.data[DOMAIN][entry_id][VS_COORDINATOR].async_request_refresh()

    services: list[tuple[str, Any]] = [
        (SERVICE_FRYER_COOK, _async_fryer_cook),
        (SERVICE_FRYER_SET_PREHEAT, _async_fryer_set_preheat),
        (SERVICE_FRYER_COOK_FROM_PREHEAT, _async_fryer_cook_from_preheat),
        (SERVICE_THERMOSTAT_CANCEL_HOLD, _async_thermostat_cancel_hold),
        (SERVICE_THERMOSTAT_SET_LOCK, _async_thermostat_set_lock),
        (SERVICE_THERMOSTAT_SET_ECO_TYPE, _async_thermostat_set_eco_type),
    ]

    for service_name, handler in services:
        if hass.services.has_service(DOMAIN, service_name):
            continue
        hass.services.async_register(DOMAIN, service_name, handler)
        _LOGGER.debug("Registered service %s.%s", DOMAIN, service_name)


def async_remove_services(hass: HomeAssistant) -> None:
    """Remove VeSync services if registered."""

    for service_name in (
        SERVICE_FRYER_COOK,
        SERVICE_FRYER_SET_PREHEAT,
        SERVICE_FRYER_COOK_FROM_PREHEAT,
        SERVICE_THERMOSTAT_CANCEL_HOLD,
        SERVICE_THERMOSTAT_SET_LOCK,
        SERVICE_THERMOSTAT_SET_ECO_TYPE,
    ):
        if hass.services.has_service(DOMAIN, service_name):
            hass.services.async_remove(DOMAIN, service_name)
