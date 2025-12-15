"""Support for VeSync thermostats."""

import logging
from typing import Any

from pyvesync.base_devices.thermostat_base import VeSyncThermostat
from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice
from pyvesync.const import ThermostatFanModes, ThermostatWorkModes

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_ON,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_WHOLE,
    UnitOfTemperature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_thermostat, iter_manager_devices
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)

FAN_CIRCULATE = "circulate"


def _coerce_work_mode(work_mode: ThermostatWorkModes | str | None) -> ThermostatWorkModes | None:
    if work_mode is None:
        return None
    if isinstance(work_mode, ThermostatWorkModes):
        return work_mode
    if isinstance(work_mode, str):
        normalized = work_mode.strip().lower()
        mapping: dict[str, ThermostatWorkModes] = {
            "off": ThermostatWorkModes.OFF,
            "heat": ThermostatWorkModes.HEAT,
            "emheat": ThermostatWorkModes.EM_HEAT,
            "em_heat": ThermostatWorkModes.EM_HEAT,
            "em heat": ThermostatWorkModes.EM_HEAT,
            "cool": ThermostatWorkModes.COOL,
            "auto": ThermostatWorkModes.AUTO,
            "smart_auto": ThermostatWorkModes.SMART_AUTO,
            "smart auto": ThermostatWorkModes.SMART_AUTO,
        }
        return mapping.get(normalized)
    return None


def _temp_unit_from_device(device: VeSyncThermostat) -> UnitOfTemperature:
    unit = getattr(getattr(device, "state", None), "temperature_unit", None)
    if isinstance(unit, str) and unit.lower().startswith("c"):
        return UnitOfTemperature.CELSIUS
    return UnitOfTemperature.FAHRENHEIT


def _work_mode_to_hvac_mode(work_mode: ThermostatWorkModes | None) -> HVACMode:
    if work_mode in (None, ThermostatWorkModes.OFF):
        return HVACMode.OFF
    if work_mode in (ThermostatWorkModes.HEAT, ThermostatWorkModes.EM_HEAT):
        return HVACMode.HEAT
    if work_mode == ThermostatWorkModes.COOL:
        return HVACMode.COOL
    if work_mode in (ThermostatWorkModes.AUTO, ThermostatWorkModes.SMART_AUTO):
        return HVACMode.AUTO
    return HVACMode.OFF


def _hvac_mode_to_work_mode(hvac_mode: HVACMode) -> ThermostatWorkModes:
    if hvac_mode == HVACMode.HEAT:
        return ThermostatWorkModes.HEAT
    if hvac_mode == HVACMode.COOL:
        return ThermostatWorkModes.COOL
    if hvac_mode == HVACMode.AUTO:
        return ThermostatWorkModes.AUTO
    return ThermostatWorkModes.OFF


def _fan_mode_to_ha(fan_mode: ThermostatFanModes | None) -> str | None:
    if fan_mode is None:
        return None
    if fan_mode == ThermostatFanModes.AUTO:
        return FAN_AUTO
    if fan_mode == ThermostatFanModes.ON:
        return FAN_ON
    if fan_mode == ThermostatFanModes.CIRCULATE:
        return FAN_CIRCULATE
    return None


def _ha_to_fan_mode(fan_mode: str) -> ThermostatFanModes | None:
    if fan_mode == FAN_AUTO:
        return ThermostatFanModes.AUTO
    if fan_mode == FAN_ON:
        return ThermostatFanModes.ON
    if fan_mode == FAN_CIRCULATE:
        return ThermostatFanModes.CIRCULATE
    return None



async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the VeSync climate platform."""

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
    coordinator: DataUpdateCoordinator,
) -> None:
    """Add climate entities."""
    entities = []
    for dev in devices:
        if is_thermostat(dev):
            entities.append(VeSyncClimate(dev, coordinator))

    async_add_entities(entities)


class VeSyncClimate(VeSyncBaseEntity, ClimateEntity):
    """Representation of a VeSync thermostat."""

    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE
    )
    _attr_precision = PRECISION_WHOLE
    _attr_translation_key = "vesync_climate"

    def __init__(
        self,
        device: VeSyncBaseDevice,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the thermostat."""
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{self.base_unique_id}-climate"

        # Cache fixed metadata
        self._attr_temperature_unit = _temp_unit_from_device(self._thermostat)

        fan_modes: list[str] = []
        for mode in getattr(self._thermostat, "fan_modes", []) or []:
            if isinstance(mode, ThermostatFanModes):
                vs_mode = mode
            elif isinstance(mode, str):
                vs_mode = _ha_to_fan_mode(mode.strip().lower())
            elif hasattr(mode, "value") and isinstance(getattr(mode, "value"), str):
                vs_mode = _ha_to_fan_mode(getattr(mode, "value").strip().lower())
            else:
                vs_mode = None

            ha_mode = _fan_mode_to_ha(vs_mode)
            if ha_mode is not None and ha_mode not in fan_modes:
                fan_modes.append(ha_mode)

        # Defensive fallback: do not expose circulate unless explicitly supported.
        self._attr_fan_modes = fan_modes or [FAN_AUTO, FAN_ON]

        supported: list[HVACMode] = [HVACMode.OFF]
        for mode in getattr(self._thermostat, "supported_work_modes", []) or []:
            coerced = _coerce_work_mode(mode)
            if coerced is None and hasattr(mode, "value"):
                coerced = _coerce_work_mode(getattr(mode, "value"))

            hvac_mode = _work_mode_to_hvac_mode(coerced)
            if hvac_mode not in supported:
                supported.append(hvac_mode)
        self._attr_hvac_modes = supported

    @property
    def _thermostat(self) -> VeSyncThermostat:
        return self.device  # type: ignore[return-value]

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return getattr(self._thermostat.state, "temperature", None)

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        work_mode = _coerce_work_mode(getattr(self._thermostat.state, "work_mode", None))
        if work_mode in (ThermostatWorkModes.HEAT, ThermostatWorkModes.EM_HEAT):
            return getattr(self._thermostat.state, "heat_to_temp", None)
        if work_mode == ThermostatWorkModes.COOL:
            return getattr(self._thermostat.state, "cool_to_temp", None)

        # AUTO/SMART_AUTO: HA's single target temperature model doesn't map cleanly.
        # Return a reasonable fallback so the entity remains usable.
        return (
            getattr(self._thermostat.state, "heat_to_temp", None)
            or getattr(self._thermostat.state, "cool_to_temp", None)
        )

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return hvac operation ie. heat, cool mode."""
        return _work_mode_to_hvac_mode(
            _coerce_work_mode(getattr(self._thermostat.state, "work_mode", None))
        )

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        state = getattr(self._thermostat, "state", None)
        if state is None:
            return None

        if getattr(state, "is_heating", False):
            return HVACAction.HEATING
        if getattr(state, "is_cooling", False):
            return HVACAction.COOLING
        if getattr(state, "is_running", False):
            return HVACAction.FAN
        return HVACAction.IDLE

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        return _fan_mode_to_ha(getattr(self._thermostat.state, "fan_mode", None))

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        if (temp := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        temperature = int(temp)
        work_mode = _coerce_work_mode(getattr(self._thermostat.state, "work_mode", None))

        if work_mode == ThermostatWorkModes.COOL and hasattr(self._thermostat, "set_cool_to_temp"):
            success = await self._thermostat.set_cool_to_temp(temperature)
        elif work_mode in (ThermostatWorkModes.HEAT, ThermostatWorkModes.EM_HEAT) and hasattr(
            self._thermostat, "set_heat_to_temp"
        ):
            success = await self._thermostat.set_heat_to_temp(temperature)
        elif hasattr(self._thermostat, "set_temp_point"):
            success = await self._thermostat.set_temp_point(temperature)
        else:
            _LOGGER.debug("Thermostat %s does not support setting temperature", self.device.device_name)
            return

        if not success:
            raise HomeAssistantError(getattr(self.device, "last_response", None) and self.device.last_response.message or "Unable to set temperature")

        await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target hvac mode."""
        work_mode = _hvac_mode_to_work_mode(hvac_mode)
        if not hasattr(self._thermostat, "set_mode"):
            return

        success = await self._thermostat.set_mode(work_mode)
        if not success:
            raise HomeAssistantError(getattr(self.device, "last_response", None) and self.device.last_response.message or "Unable to set HVAC mode")

        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set new target fan mode."""
        vs_fan_mode = _ha_to_fan_mode(fan_mode)
        if vs_fan_mode is None:
            return

        if not hasattr(self._thermostat, "set_fan_mode"):
            return

        success = await self._thermostat.set_fan_mode(vs_fan_mode)
        if not success:
            raise HomeAssistantError(getattr(self.device, "last_response", None) and self.device.last_response.message or "Unable to set fan mode")

        await self.coordinator.async_request_refresh()
