"""Class to manage VeSync data updates."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from pyvesync import VeSync

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import UPDATE_INTERVAL, UPDATE_INTERVAL_ENERGY

_LOGGER = logging.getLogger(__name__)


class VeSyncStateCoordinator(DataUpdateCoordinator[None]):
    """Class representing state data coordinator for VeSync devices."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, manager: VeSync
    ) -> None:
        """Initialize."""
        self._manager = manager

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="VeSyncStateCoordinator",
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Refreshing VeSync device state")
        await self._manager.update_all_devices()
        _LOGGER.debug("VeSync state refresh complete")


class VeSyncEnergyCoordinator(DataUpdateCoordinator[None]):
    """Class representing energy data coordinator for VeSync devices."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, config_entry: ConfigEntry, manager: VeSync
    ) -> None:
        """Initialize."""
        self._manager = manager

        super().__init__(
            hass,
            _LOGGER,
            config_entry=config_entry,
            name="VeSyncEnergyCoordinator",
            update_interval=timedelta(seconds=UPDATE_INTERVAL_ENERGY),
        )

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        _LOGGER.debug("Refreshing VeSync energy data")
        if hasattr(self._manager.devices, "outlets"):
             await asyncio.gather(
                *(outlet.update_energy() for outlet in self._manager.devices.outlets)
            )
        _LOGGER.debug("VeSync energy refresh complete")
