"""Support for VeSync firmware updates."""
import logging
from typing import Any

from homeassistant.components.update import (
    UpdateDeviceClass,
    UpdateEntity,
    UpdateEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync update platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    # Iterate all devices to check for firmware updates
    all_devices = (
        getattr(manager, "fans", []) +
        getattr(manager, "outlets", []) +
        getattr(manager, "switches", []) +
        getattr(manager, "bulbs", []) +
        getattr(manager, "kitchen", []) +
        getattr(manager, "thermostats", [])
    )

    for device in all_devices:
        devices.append(VeSyncUpdate(device, coordinator))

    async_add_entities(devices)

class VeSyncUpdate(VeSyncBaseEntity, UpdateEntity):
    """Representation of a VeSync firmware update."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_supported_features = UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_firmware"
        self._attr_name = f"{device.device_name} Firmware"

    @property
    def installed_version(self) -> str | None:
        """Version installed and in use."""
        return self.device.current_firm_version

    @property
    def latest_version(self) -> str | None:
        """Latest version available for install."""
        # Assuming pyvesync has a way to check for updates, usually it's in the device details
        # If not available, assume current is latest
        # This is a placeholder logic as pyvesync update checking might vary
        return self.device.current_firm_version 

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        """Install an update."""
        # Implement firmware update logic if supported by pyvesync
        await self.device.update_firmware()
        self.coordinator.async_set_updated_data(self.coordinator.data)
