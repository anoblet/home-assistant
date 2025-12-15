"""Common entity for VeSync Component."""

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .common import get_base_unique_id
from .const import DOMAIN


class VeSyncBaseEntity(CoordinatorEntity[DataUpdateCoordinator[None]]):
    """Base class for VeSync Entity Representations."""

    _attr_has_entity_name = True

    def __init__(
        self, device: VeSyncBaseDevice, coordinator: DataUpdateCoordinator[None]
    ) -> None:
        """Initialize the VeSync device."""
        super().__init__(coordinator)
        self.device = device
        self._attr_unique_id = self.base_unique_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.base_unique_id)},
            name=self.device.device_name,
            model=self.device.device_type,
            manufacturer="VeSync",
            sw_version=self.device.current_firm_version,
        )

    @property
    def base_unique_id(self):
        """Return the ID of this device."""
        # The unique_id property may be overridden in subclasses, such as in
        # sensors. Maintaining base_unique_id allows us to group related
        # entities under a single device.
        return get_base_unique_id(self.device)

    @property
    def available(self) -> bool:
        """Return True if device is available."""
        if not super().available:
            return False

        state = getattr(self.device, "state", None)
        connection_status = getattr(state, "connection_status", None)
        if connection_status is None:
            return True
        return connection_status == "online"
