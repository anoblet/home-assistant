"""Coordinator for VeSync integration."""
import logging
from datetime import timedelta

from pyvesync import VeSync

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, VS_UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)

class VeSyncDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching VeSync data."""

    def __init__(self, hass: HomeAssistant, manager: VeSync) -> None:
        """Initialize global VeSync data updater."""
        self.manager = manager
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=VS_UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Fetch data from VeSync."""
        try:
            await self.manager.update()
            if self.manager.devices:
                _LOGGER.debug("VeSync devices updated. Total devices: %d", len(self.manager.devices))
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
