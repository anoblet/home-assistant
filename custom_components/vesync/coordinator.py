"""Class to manage VeSync data updates."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from pyvesync import VeSync
from pyvesync.utils.errors import VeSyncError, VeSyncLoginError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

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
        try:
            await self._manager.update_all_devices()
        except VeSyncLoginError as err:
            raise ConfigEntryAuthFailed("VeSync authentication failed") from err
        except VeSyncError as err:
            raise UpdateFailed(f"VeSync state refresh failed: {err}") from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"VeSync state refresh failed: {err}") from err
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
        try:
            outlets = getattr(getattr(self._manager, "devices", None), "outlets", None)
            if not outlets:
                _LOGGER.debug("No VeSync outlets found for energy refresh")
                return

            results = await asyncio.gather(
                *(outlet.update_energy() for outlet in outlets),
                return_exceptions=True,
            )

            failures: list[Exception] = []
            for outlet, result in zip(outlets, results):
                if isinstance(result, Exception):
                    failures.append(result)
                    _LOGGER.debug(
                        "VeSync energy refresh failed for outlet %s (cid=%s): %s",
                        getattr(outlet, "device_name", None),
                        getattr(outlet, "cid", None),
                        f"{type(result).__name__}: {result}",
                    )

            if failures:
                _LOGGER.debug(
                    "VeSync energy refresh completed with %s failures", len(failures)
                )
        except VeSyncLoginError as err:
            raise ConfigEntryAuthFailed("VeSync authentication failed") from err
        except VeSyncError as err:
            raise UpdateFailed(f"VeSync energy refresh failed: {err}") from err
        except Exception as err:  # noqa: BLE001
            raise UpdateFailed(f"VeSync energy refresh failed: {err}") from err
        _LOGGER.debug("VeSync energy refresh complete")
