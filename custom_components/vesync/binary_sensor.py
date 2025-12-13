"""Support for VeSync binary sensors."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .common import is_air_fryer
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync binary sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    entities = []

    if hasattr(manager, "kitchen"):
        for device in manager.kitchen:
            if is_air_fryer(device.device_type):
                entities.append(VeSyncAirFryerIsCookingBinarySensor(device, coordinator))
                entities.append(VeSyncAirFryerIsHeatingBinarySensor(device, coordinator))

    async_add_entities(entities)

class VeSyncAirFryerIsCookingBinarySensor(VeSyncBaseEntity, BinarySensorEntity):
    """Air Fryer Is Cooking Binary Sensor."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_is_cooking"
        self._attr_name = f"{device.device_name} Is Cooking"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.device.fryer_status.get("is_cooking", False)

class VeSyncAirFryerIsHeatingBinarySensor(VeSyncBaseEntity, BinarySensorEntity):
    """Air Fryer Is Heating Binary Sensor."""

    _attr_device_class = BinarySensorDeviceClass.HEAT

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_is_heating"
        self._attr_name = f"{device.device_name} Is Heating"

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return self.device.fryer_status.get("is_heating", False)
