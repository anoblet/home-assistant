"""Update entity for VeSync.."""

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.update import UpdateDeviceClass, UpdateEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import iter_manager_devices
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up update entity."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id][VS_COORDINATOR]

    @callback
    def discover(devices: list[VeSyncBaseDevice]) -> None:
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_DEVICES), discover)
    )

    manager = hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER]
    _setup_entities(iter_manager_devices(manager), async_add_entities, coordinator)


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: VeSyncDataCoordinator,
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

    def __init__(self, device: VeSyncBaseDevice, coordinator: VeSyncDataCoordinator) -> None:
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
