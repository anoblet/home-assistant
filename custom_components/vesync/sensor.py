"""Support for voltage, power & energy sensors for VeSync outlets."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import logging

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .common import is_fryer, is_humidifier, is_outlet, is_purifier, iter_manager_devices, rgetattr
from .const import DOMAIN, VS_COORDINATOR, VS_COORDINATOR_ENERGY, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class VeSyncSensorEntityDescription(SensorEntityDescription):
    """Describe VeSync sensor entity."""

    value_fn: Callable[[VeSyncBaseDevice], StateType]

    exists_fn: Callable[[VeSyncBaseDevice], bool]


SENSORS: tuple[VeSyncSensorEntityDescription, ...] = (
    VeSyncSensorEntityDescription(
        key="filter-life",
        translation_key="filter_life",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda device: device.state.filter_life,
        exists_fn=lambda device: rgetattr(device, "state.filter_life") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="air-quality",
        translation_key="air_quality",
        value_fn=lambda device: device.state.air_quality_string,
        exists_fn=(
            lambda device: rgetattr(device, "state.air_quality_string") is not None
        ),
    ),
    VeSyncSensorEntityDescription(
        key="pm25",
        translation_key="pm25",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.pm25,
        exists_fn=lambda device: rgetattr(device, "state.pm25") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="pm1",
        translation_key="pm1",
        device_class=getattr(SensorDeviceClass, "PM1", None),
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.pm1"),
        exists_fn=lambda device: rgetattr(device, "state.pm1") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="pm10",
        translation_key="pm10",
        device_class=getattr(SensorDeviceClass, "PM10", None),
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.pm10"),
        exists_fn=lambda device: rgetattr(device, "state.pm10") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="aq_percent",
        translation_key="air_quality_percent",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.aq_percent"),
        exists_fn=lambda device: rgetattr(device, "state.aq_percent") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="voc",
        translation_key="voc",
        native_unit_of_measurement="ppb",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.voc"),
        exists_fn=lambda device: rgetattr(device, "state.voc") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="co2",
        translation_key="co2",
        device_class=getattr(SensorDeviceClass, "CO2", None),
        native_unit_of_measurement="ppm",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.co2"),
        exists_fn=lambda device: rgetattr(device, "state.co2") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="fan_rotate_angle",
        translation_key="fan_rotate_angle",
        native_unit_of_measurement="°",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.fan_rotate_angle"),
        exists_fn=lambda device: rgetattr(device, "state.fan_rotate_angle") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="power",
        translation_key="current_power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.power,
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="energy",
        translation_key="energy_today",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda device: device.state.energy,
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="energy-weekly",
        translation_key="energy_week",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda device: getattr(
            device.state.weekly_history, "totalEnergy", None
        ),
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="energy-monthly",
        translation_key="energy_month",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda device: getattr(
            device.state.monthly_history, "totalEnergy", None
        ),
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="energy-yearly",
        translation_key="energy_year",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        value_fn=lambda device: getattr(
            device.state.yearly_history, "totalEnergy", None
        ),
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="voltage",
        translation_key="current_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.voltage,
        exists_fn=is_outlet,
    ),
    VeSyncSensorEntityDescription(
        key="humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.humidity,
        exists_fn=is_humidifier,
    ),
    VeSyncSensorEntityDescription(
        key="purifier_humidity",
        translation_key="humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.humidity"),
        exists_fn=lambda device: is_purifier(device) and rgetattr(device, "state.humidity") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: device.state.temperature,
        exists_fn=lambda device: is_humidifier(device)
        and device.state.temperature is not None,
    ),
    VeSyncSensorEntityDescription(
        key="purifier_temperature",
        translation_key="temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.temperature"),
        exists_fn=lambda device: is_purifier(device) and rgetattr(device, "state.temperature") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="current_temperature",
        translation_key="current_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.FAHRENHEIT,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.current_temp"),
        exists_fn=lambda device: is_fryer(device)
        and rgetattr(device, "state.current_temp") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="cook_time_remaining",
        translation_key="cook_time_remaining",
        native_unit_of_measurement="min",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda device: rgetattr(device, "state.cook_time_remaining"),
        exists_fn=lambda device: is_fryer(device)
        and rgetattr(device, "state.cook_time_remaining") is not None,
    ),
    VeSyncSensorEntityDescription(
        key="kitchen_mode",
        translation_key="kitchen_mode",
        value_fn=lambda device: rgetattr(device, "state.cook_status"),
        exists_fn=lambda device: is_fryer(device)
        and rgetattr(device, "state.cook_status") is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switches."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][VS_COORDINATOR]
    energy_coordinator = hass.data[DOMAIN][config_entry.entry_id][VS_COORDINATOR_ENERGY]

    @callback
    def discover(devices: list[VeSyncBaseDevice]) -> None:
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator, energy_coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_DEVICES), discover)
    )

    manager = hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER]
    _setup_entities(iter_manager_devices(manager), async_add_entities, coordinator, energy_coordinator)


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: DataUpdateCoordinator,
    energy_coordinator: DataUpdateCoordinator,
) -> None:
    """Check if device is online and add entity."""
    entities = []
    for dev in devices:
        for description in SENSORS:
            if description.exists_fn(dev):
                if description.key in ("energy-weekly", "energy-monthly", "energy-yearly"):
                    entities.append(VeSyncSensorEntity(dev, description, energy_coordinator))
                else:
                    entities.append(VeSyncSensorEntity(dev, description, coordinator))

    async_add_entities(entities, update_before_add=True)


class VeSyncSensorEntity(VeSyncBaseEntity, SensorEntity):
    """Representation of a sensor describing a VeSync device."""

    entity_description: VeSyncSensorEntityDescription

    def __init__(
        self,
        device: VeSyncBaseDevice,
        description: VeSyncSensorEntityDescription,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the VeSync outlet device."""
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.base_unique_id}-{description.key}"

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self.device)
