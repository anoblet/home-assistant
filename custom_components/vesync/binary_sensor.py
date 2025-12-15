"""Binary Sensor for VeSync."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import EntityCategory
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_purifier, iter_manager_devices, rgetattr
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class VeSyncBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes custom binary sensor entities."""

    is_on: Callable[[VeSyncBaseDevice], bool]
    exists_fn: Callable[[VeSyncBaseDevice], bool] = lambda _: True


SENSOR_DESCRIPTIONS: tuple[VeSyncBinarySensorEntityDescription, ...] = (
    VeSyncBinarySensorEntityDescription(
        key="water_lacks",
        translation_key="water_lacks",
        is_on=lambda device: device.state.water_lacks,
        device_class=BinarySensorDeviceClass.PROBLEM,
        exists_fn=lambda device: rgetattr(device, "state.water_lacks") is not None,
    ),
    VeSyncBinarySensorEntityDescription(
        key="water_tank_lifted",
        translation_key="water_tank_lifted",
        is_on=lambda device: device.state.water_tank_lifted,
        device_class=BinarySensorDeviceClass.PROBLEM,
        exists_fn=(
            lambda device: rgetattr(device, "state.water_tank_lifted") is not None
        ),
    ),
    VeSyncBinarySensorEntityDescription(
        key="filter_open_state",
        translation_key="filter_open_state",
        is_on=lambda device: bool(rgetattr(device, "state.filter_open_state")),
        device_class=BinarySensorDeviceClass.PROBLEM,
        entity_category=EntityCategory.DIAGNOSTIC,
        exists_fn=lambda device: is_purifier(device) and rgetattr(device, "state.filter_open_state") is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary_sensor platform."""

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
    """Add entity."""
    async_add_entities(
        (
            VeSyncBinarySensor(dev, description, coordinator)
            for dev in devices
            for description in SENSOR_DESCRIPTIONS
            if description.exists_fn(dev)
        ),
    )


class VeSyncBinarySensor(BinarySensorEntity, VeSyncBaseEntity):
    """Vesync binary sensor class."""

    entity_description: VeSyncBinarySensorEntityDescription

    def __init__(
        self,
        device: VeSyncBaseDevice,
        description: VeSyncBinarySensorEntityDescription,
        coordinator: VeSyncDataCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on(self.device)
