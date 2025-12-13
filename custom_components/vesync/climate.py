"""Support for VeSync Thermostats."""
import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, VS_THERMOSTAT
from .common import is_thermostat
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

VESYNC_TO_HA_MODE = {
    "heat": HVACMode.HEAT,
    "cool": HVACMode.COOL,
    "auto": HVACMode.AUTO,
    "off": HVACMode.OFF,
}

HA_TO_VESYNC_MODE = {v: k for k, v in VESYNC_TO_HA_MODE.items()}

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the VeSync climate platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    manager = coordinator.manager

    devices = []
    # Check if manager has thermostats attribute, otherwise iterate all devices
    if hasattr(manager.devices, "thermostats"):
        for device in manager.devices.thermostats:
            devices.append(VeSyncThermostat(device, coordinator))
    else:
        # Fallback if pyvesync structure is different
        pass

    async_add_entities(devices)

class VeSyncThermostat(VeSyncBaseEntity, ClimateEntity):
    """Representation of a VeSync Thermostat."""

    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL, HVACMode.AUTO]
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.FAHRENHEIT # VeSync usually uses F

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self.device.details.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        mode = self.device.details.get("work_mode")
        if mode == "heat":
            return self.device.details.get("heat_to_temp")
        elif mode == "cool":
            return self.device.details.get("cool_to_temp")
        return None

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        mode = self.device.details.get("work_mode")
        return VESYNC_TO_HA_MODE.get(mode)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        
        # Determine which temp to set based on current mode
        mode = self.device.details.get("work_mode")
        if mode == "heat":
            await self.device.set_target_temp(temp, "heat")
        elif mode == "cool":
            await self.device.set_target_temp(temp, "cool")
        
        self.coordinator.async_set_updated_data(self.coordinator.data)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        if hvac_mode not in HA_TO_VESYNC_MODE:
            return
        
        vs_mode = HA_TO_VESYNC_MODE[hvac_mode]
        await self.device.set_mode(vs_mode)
        self.coordinator.async_set_updated_data(self.coordinator.data)
