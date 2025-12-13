"""Support for VeSync thermostats."""
import logging
from typing import Any

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
    FAN_AUTO,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_HIGH,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
    PRECISION_WHOLE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

VS_TO_HA_MODE_MAP = {
    "auto": HVACMode.AUTO,
    "cool": HVACMode.COOL,
    "heat": HVACMode.HEAT,
    "off": HVACMode.OFF,
}

HA_TO_VS_MODE_MAP = {v: k for k, v in VS_TO_HA_MODE_MAP.items()}

VS_TO_HA_FAN_MODE_MAP = {
    "auto": FAN_AUTO,
    "low": FAN_LOW,
    "medium": FAN_MEDIUM,
    "high": FAN_HIGH,
}

HA_TO_VS_FAN_MODE_MAP = {v: k for k, v in VS_TO_HA_FAN_MODE_MAP.items()}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the VeSync climate platform."""

    coordinator = hass.data[DOMAIN][VS_COORDINATOR]

    @callback
    def discover(devices: list[VeSyncBaseDevice]) -> None:
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_DEVICES), discover)
    )

    # We need to make sure we get thermostats. 
    # If manager.devices doesn't include them, we might need to access manager.thermostats
    manager = hass.data[DOMAIN][VS_MANAGER]
    devices = list(manager.devices)
    if hasattr(manager, "thermostats"):
        devices.extend([d for d in manager.thermostats if d not in devices])

    _setup_entities(
        devices, async_add_entities, coordinator
    )


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: VeSyncDataCoordinator,
) -> None:
    """Add climate entities."""
    entities = []
    for dev in devices:
        if "thermostat" in dev.device_type.lower():
             entities.append(VeSyncClimate(dev, coordinator))
    
    async_add_entities(entities)


class VeSyncClimate(VeSyncBaseEntity, ClimateEntity):
    """Representation of a VeSync thermostat."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
    )
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT
    _attr_precision = PRECISION_WHOLE
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
    _attr_fan_modes = [FAN_AUTO, FAN_LOW, FAN_MEDIUM, FAN_HIGH]
    _attr_translation_key = "vesync_climate"

    def __init__(
        self,
        device: VeSyncBaseDevice,
        coordinator: VeSyncDataCoordinator,
    ) -> None:
        """Initialize the thermostat."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{super().unique_id}-climate"

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # Try different attributes
        if hasattr(self.device, "details"):
            return self.device.details.get("current_temp")
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        if hasattr(self.device, "details"):
            return self.device.details.get("target_temp")
        return None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        if hasattr(self.device, "details"):
            mode = self.device.details.get("mode")
            return VS_TO_HA_MODE_MAP.get(mode)
        return None

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        if hasattr(self.device, "details"):
            mode = self.device.details.get("fan_mode")
            return VS_TO_HA_FAN_MODE_MAP.get(mode)
        return None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self.device.set_target_temp(int(temp))
        self.schedule_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        vs_mode = HA_TO_VS_MODE_MAP.get(hvac_mode)
        if vs_mode:
            await self.device.set_mode(vs_mode)
            self.schedule_update_ha_state()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        vs_mode = HA_TO_VS_FAN_MODE_MAP.get(fan_mode)
        if vs_mode:
            await self.device.set_fan_mode(vs_mode)
            self.schedule_update_ha_state()
