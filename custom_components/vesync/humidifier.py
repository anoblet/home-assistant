"""Support for VeSync humidifiers."""
import logging
from typing import Any

from homeassistant.components.humidifier import (
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VS_HUMIDIFIER
from .common import is_humidifier
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync humidifier platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    # Iterate over all devices and check if they are humidifiers
    # This handles both list and DeviceContainer for manager.devices
    if manager.devices:
        for device in manager.devices:
            if is_humidifier(device.device_type):
                devices.append(VeSyncHumidifier(device, coordinator))

    async_add_entities(devices)

class VeSyncHumidifier(VeSyncBaseEntity, HumidifierEntity):
    """Representation of a VeSync humidifier."""

    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER
    _attr_supported_features = HumidifierEntityFeature.MODES

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return getattr(self.device, "device_status", "off") == "on"

    @property
    def target_humidity(self) -> int | None:
        """Return the humidity we try to reach."""
        config = getattr(self.device, "config", {})
        return int(config.get("auto_target_humidity", 0))

    @property
    def mode(self) -> str | None:
        """Return the current mode."""
        return getattr(self.device, "mode", None)

    @property
    def available_modes(self) -> list[str] | None:
        """Return a list of available modes."""
        return ["auto", "manual", "sleep"]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        await self.device.turn_on()
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.device.turn_off()
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_set_humidity(self, humidity: int) -> None:
        """Set new target humidity."""
        await self.device.set_humidity(humidity)
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_set_mode(self, mode: str) -> None:
        """Set new mode."""
        if mode == "auto":
            await self.device.set_auto_mode()
        elif mode == "manual":
            await self.device.set_manual_mode()
        elif mode == "sleep":
            await self.device.set_sleep_mode()
        self.coordinator.async_set_updated_data(self.coordinator.data)
