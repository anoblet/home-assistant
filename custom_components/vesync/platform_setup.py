"""Shared platform setup helpers for the VeSync integration.

This module centralizes the common boilerplate used by the various entity
platforms (switch, sensor, etc.) when setting up from a config entry.
"""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .common import iter_manager_devices
from .const import (
    DOMAIN,
    VS_COORDINATOR,
    VS_COORDINATOR_ENERGY,
    VS_DEVICES,
    VS_DISCOVERY,
    VS_MANAGER,
)

_LOGGER = logging.getLogger(__name__)


SetupEntitiesFn = Callable[
    [list[VeSyncBaseDevice], AddConfigEntryEntitiesCallback, DataUpdateCoordinator],
    None,
]

SetupEntitiesWithEnergyFn = Callable[
    [
        list[VeSyncBaseDevice],
        AddConfigEntryEntitiesCallback,
        DataUpdateCoordinator,
        DataUpdateCoordinator,
    ],
    None,
]


def _get_domain_data(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    domain_data = hass.data.get(DOMAIN)
    if not domain_data or entry.entry_id not in domain_data:
        raise RuntimeError("VeSync domain data is not initialized")
    return domain_data[entry.entry_id]


async def async_setup_vesync_platform_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    setup_entities: SetupEntitiesFn,
) -> None:
    """Set up a platform for a VeSync config entry.

    - Adds entities for current devices.
    - Subscribes to new-device discovery signals.
    """

    entry_data = _get_domain_data(hass, config_entry)
    manager = entry_data[VS_MANAGER]
    coordinator: DataUpdateCoordinator = entry_data[VS_COORDINATOR]

    devices = [
        d for d in iter_manager_devices(manager) if isinstance(d, VeSyncBaseDevice)
    ]
    setup_entities(devices, async_add_entities, coordinator)

    @callback
    def _async_discovered(new_devices: list[VeSyncBaseDevice]) -> None:
        _LOGGER.debug("VeSync discovered %s devices for platform", len(new_devices))
        setup_entities(new_devices, async_add_entities, coordinator)

    unsub = async_dispatcher_connect(
        hass,
        VS_DISCOVERY.format(VS_DEVICES),
        _async_discovered,
    )
    config_entry.async_on_unload(unsub)


async def async_setup_vesync_platform_entry_with_energy(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
    setup_entities: SetupEntitiesWithEnergyFn,
) -> None:
    """Set up a platform for a VeSync config entry with energy coordinator."""

    entry_data = _get_domain_data(hass, config_entry)
    manager = entry_data[VS_MANAGER]
    coordinator: DataUpdateCoordinator = entry_data[VS_COORDINATOR]
    energy_coordinator: DataUpdateCoordinator = entry_data[VS_COORDINATOR_ENERGY]

    devices = [
        d for d in iter_manager_devices(manager) if isinstance(d, VeSyncBaseDevice)
    ]
    setup_entities(devices, async_add_entities, coordinator, energy_coordinator)

    @callback
    def _async_discovered(new_devices: list[VeSyncBaseDevice]) -> None:
        _LOGGER.debug(
            "VeSync discovered %s devices for platform (with energy)",
            len(new_devices),
        )
        setup_entities(new_devices, async_add_entities, coordinator, energy_coordinator)

    unsub = async_dispatcher_connect(
        hass,
        VS_DISCOVERY.format(VS_DEVICES),
        _async_discovered,
    )
    config_entry.async_on_unload(unsub)
