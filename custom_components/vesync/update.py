"""Update entity for VeSync.."""

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.update import UpdateDeviceClass, UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .entity import VeSyncBaseEntity
from .platform_setup import async_setup_vesync_platform_entry


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up update entity."""

    await async_setup_vesync_platform_entry(
        hass,
        config_entry,
        async_add_entities,
        _setup_entities,
    )


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: DataUpdateCoordinator,
) -> None:
    """Add update entities."""

    async_add_entities(
        VeSyncDeviceUpdate(
            device=device,
            coordinator=coordinator,
        )
        for device in devices
    )


class VeSyncDeviceUpdate(VeSyncBaseEntity, UpdateEntity):
    """Representation of a VeSync device update entity."""

    _attr_device_class = UpdateDeviceClass.FIRMWARE
    _attr_name = "Firmware"

    def __init__(self, device: VeSyncBaseDevice, coordinator: DataUpdateCoordinator) -> None:
        """Initialize the update entity."""
        super().__init__(device, coordinator)
        # Never use the bare device base id for update entities; it collides with
        # primary entities (fan/humidifier/light/etc.).
        self._attr_unique_id = f"{self.base_unique_id}-firmware"

    @property
    def installed_version(self) -> str | None:
        """Return installed_version."""
        return self.device.current_firm_version

    @property
    def latest_version(self) -> str | None:
        """Return latest_version."""
        return self.device.latest_firm_version
