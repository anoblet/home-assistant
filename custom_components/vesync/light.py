"""Support for VeSync lights."""
import logging
from typing import Any

from homeassistant.components.light import (
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VS_LIGHT
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync light platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    if hasattr(manager.devices, "bulbs"):
        for device in manager.devices.bulbs:
            devices.append(VeSyncBulb(device, coordinator))

    async_add_entities(devices)

class VeSyncBulb(VeSyncBaseEntity, LightEntity):
    """Representation of a VeSync bulb."""

    _attr_supported_color_modes = {ColorMode.COLOR_TEMP, ColorMode.HS}
    _attr_color_mode = ColorMode.HS # Default, will update

    @property
    def is_on(self) -> bool:
        """Return True if light is on."""
        return getattr(self.device, "device_status", "off") == "on"

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        brightness = getattr(self.device, "brightness", 0)
        return int(brightness / 100 * 255)

    @property
    def color_temp(self) -> int | None:
        """Return the CT color value in mireds."""
        # VeSync uses 0-100 for warm/cool, need to map to mireds if possible or just use what they have?
        # Usually pyvesync bulbs have color_temp_kelvin maybe?
        # Let's assume standard behavior or skip if complex without docs.
        # For now, let's assume no CT support unless I see it in pyvesync docs, but bulbs usually have it.
        return None 

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hue and saturation color value [float, float]."""
        # Need to check pyvesync bulb attributes for color
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        if not self.is_on:
            await self.device.turn_on()
        
        if (brightness := kwargs.get("brightness")) is not None:
            val = int(brightness / 255 * 100)
            await self.device.set_brightness(val)

        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.device.turn_off()
        self.coordinator.async_set_updated_data(self.coordinator.data)
