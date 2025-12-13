"""Support for VeSync fans."""
import logging
import math
from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DOMAIN, VS_FAN
from .common import is_fan
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync fan platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    # Iterate over all devices and check if they are fans
    # This handles both list and DeviceContainer for manager.devices
    if manager.devices:
        for device in manager.devices:
            if is_fan(device.device_type):
                devices.append(VeSyncFan(device, coordinator))

    async_add_entities(devices)

class VeSyncFan(VeSyncBaseEntity, FanEntity):
    """Representation of a VeSync fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED | FanEntityFeature.PRESET_MODE

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return getattr(self.device, "device_status", "off") == "on"

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        mode = getattr(self.device, "mode", None)
        if mode == "manual":
            current_level = getattr(self.device, "fan_level", 0)
            return ranged_value_to_percentage((1, 3), current_level) # Assuming 3 speeds for now
        return None

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = getattr(self.device, "mode", None)
        if mode != "manual":
            return mode
        return None

    @property
    def preset_modes(self) -> list[str] | None:
        """Return a list of available preset modes."""
        return ["auto", "sleep"] # Common modes

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return 3 # Common for VeSync

    async def async_turn_on(self, percentage: int | None = None, preset_mode: str | None = None, **kwargs: Any) -> None:
        """Turn the fan on."""
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
            return
        
        if percentage is not None:
            await self.async_set_percentage(percentage)
            return

        await self.device.turn_on()
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.device.turn_off()
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed percentage of the fan."""
        if percentage == 0:
            await self.async_turn_off()
            return
        
        speed = math.ceil(percentage_to_ranged_value((1, 3), percentage))
        await self.device.change_fan_speed(speed)
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the preset mode of the fan."""
        if preset_mode == "auto":
            await self.device.auto_mode()
        elif preset_mode == "sleep":
            await self.device.sleep_mode()
        self.coordinator.async_set_updated_data(self.coordinator.data)
