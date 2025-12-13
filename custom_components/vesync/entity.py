"""VeSync Entity."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

class VeSyncBaseEntity(CoordinatorEntity, Entity):
    """Base class for VeSync entities."""

    def __init__(self, device, coordinator):
        """Initialize the VeSync entity."""
        super().__init__(coordinator)
        self.device = device
        self._attr_unique_id = device.cid
        self._attr_name = device.device_name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.cid)},
            "name": device.device_name,
            "model": device.device_type,
            "manufacturer": "VeSync",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return getattr(self.device, "connection_status", "online") == "online"
