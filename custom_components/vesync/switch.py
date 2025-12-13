"""Support for VeSync switches."""
import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VS_SWITCH
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync switch platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    if hasattr(manager.devices, "outlets"):
        for device in manager.devices.outlets:
            devices.append(VeSyncSwitch(device, coordinator))
    
    if hasattr(manager.devices, "switches"):
        for device in manager.devices.switches:
            devices.append(VeSyncSwitch(device, coordinator))

    async_add_entities(devices)

class VeSyncSwitch(VeSyncBaseEntity, SwitchEntity):
    """Representation of a VeSync switch."""

    @property
    def is_on(self) -> bool:
        """Return True if switch is on."""
        return getattr(self.device, "device_status", "off") == "on"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the device."""
        return {
            "active_time": getattr(self.device, "active_time", None),
            "energy": getattr(self.device, "energy_today", None),
            "power": getattr(self.device, "power", None),
            "voltage": getattr(self.device, "voltage", None),
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.device.turn_on()
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.device.turn_off()
        self.coordinator.async_set_updated_data(self.coordinator.data)
