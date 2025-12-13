"""Support for VeSync Buttons."""
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .common import is_air_fryer
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync button platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    if hasattr(manager, "kitchen"):
        for device in manager.kitchen:
            if is_air_fryer(device.device_type):
                devices.append(VeSyncAirFryerButton(device, coordinator))

    async_add_entities(devices)

class VeSyncAirFryerButton(VeSyncBaseEntity, ButtonEntity):
    """Representation of a VeSync Air Fryer Stop Button."""

    def __init__(self, device, coordinator):
        """Initialize the button."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_stop"
        self._attr_name = f"{device.device_name} Stop Cooking"

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.hass.async_add_executor_job(self.device.end)
        self.coordinator.async_set_updated_data(self.coordinator.data)
