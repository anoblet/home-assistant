"""Support for VeSync sensors."""
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfTime, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .common import is_air_fryer, is_fan
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    entities = []

    # Air Fryers
    if hasattr(manager, "kitchen"):
        for device in manager.kitchen:
            if is_air_fryer(device.device_type):
                entities.append(VeSyncAirFryerTemperatureSensor(device, coordinator))
                entities.append(VeSyncAirFryerCookTimeSensor(device, coordinator))
                entities.append(VeSyncAirFryerRemainingTimeSensor(device, coordinator))
                entities.append(VeSyncAirFryerStatusSensor(device, coordinator))
                entities.append(VeSyncAirFryerRecipeSensor(device, coordinator))

    # Fans/Purifiers
    if hasattr(manager, "fans"):
        for device in manager.fans:
            if is_fan(device.device_type):
                entities.append(VeSyncFanAirQualitySensor(device, coordinator))
                entities.append(VeSyncFanFilterLifeSensor(device, coordinator))

    async_add_entities(entities)

class VeSyncAirFryerTemperatureSensor(VeSyncBaseEntity, SensorEntity):
    """Air Fryer Current Temperature."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_current_temp"
        self._attr_name = f"{device.device_name} Current Temperature"

    @property
    def native_value(self):
        return self.device.fryer_status.get("current_temp")

class VeSyncAirFryerCookTimeSensor(VeSyncBaseEntity, SensorEntity):
    """Air Fryer Cook Set Time."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_cook_set_time"
        self._attr_name = f"{device.device_name} Cook Set Time"

    @property
    def native_value(self):
        return self.device.fryer_status.get("cook_set_time")

class VeSyncAirFryerRemainingTimeSensor(VeSyncBaseEntity, SensorEntity):
    """Air Fryer Remaining Time."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_remaining_time"
        self._attr_name = f"{device.device_name} Remaining Time"

    @property
    def native_value(self):
        return self.device.fryer_status.get("remaining_time")

class VeSyncAirFryerStatusSensor(VeSyncBaseEntity, SensorEntity):
    """Air Fryer Status."""

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_status"
        self._attr_name = f"{device.device_name} Status"

    @property
    def native_value(self):
        return self.device.fryer_status.get("cook_status")

class VeSyncAirFryerRecipeSensor(VeSyncBaseEntity, SensorEntity):
    """Air Fryer Recipe Name."""

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_recipe_name"
        self._attr_name = f"{device.device_name} Recipe Name"

    @property
    def native_value(self):
        return self.device.fryer_status.get("recipe_name")

class VeSyncFanAirQualitySensor(VeSyncBaseEntity, SensorEntity):
    """Fan Air Quality."""

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_air_quality"
        self._attr_name = f"{device.device_name} Air Quality"

    @property
    def native_value(self):
        return self.device.details.get("air_quality")

class VeSyncFanFilterLifeSensor(VeSyncBaseEntity, SensorEntity):
    """Fan Filter Life."""

    _attr_native_unit_of_measurement = "%"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, device, coordinator):
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{device.cid}_filter_life"
        self._attr_name = f"{device.device_name} Filter Life"

    @property
    def native_value(self):
        return self.device.details.get("filter_life")
