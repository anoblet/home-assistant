"""Support for VeSync humidifiers."""

import logging
from typing import Any

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.humidifier import (
    MODE_AUTO,
    MODE_NORMAL,
    MODE_SLEEP,
    HumidifierAction,
    HumidifierDeviceClass,
    HumidifierEntity,
    HumidifierEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_humidifier
from .const import (
    DOMAIN,
    VS_COORDINATOR,
    VS_DEVICES,
    VS_DISCOVERY,
    VS_HUMIDIFIER_MODE_AUTO,
    VS_HUMIDIFIER_MODE_HUMIDITY,
    VS_HUMIDIFIER_MODE_MANUAL,
    VS_HUMIDIFIER_MODE_SLEEP,
    VS_MANAGER,
)
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


VS_TO_HA_MODE_MAP = {
    VS_HUMIDIFIER_MODE_AUTO: MODE_AUTO,
    VS_HUMIDIFIER_MODE_HUMIDITY: VS_HUMIDIFIER_MODE_HUMIDITY,
    VS_HUMIDIFIER_MODE_MANUAL: MODE_NORMAL,
    VS_HUMIDIFIER_MODE_SLEEP: MODE_SLEEP,
}


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the VeSync humidifier platform."""

    coordinator = hass.data[DOMAIN][config_entry.entry_id][VS_COORDINATOR]

    @callback
    def discover(devices: list[VeSyncBaseDevice]) -> None:
        """Add new devices to platform."""
        _setup_entities(devices, async_add_entities, coordinator)

    config_entry.async_on_unload(
        async_dispatcher_connect(hass, VS_DISCOVERY.format(VS_DEVICES), discover)
    )

    manager = hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER]
    _setup_entities(manager.devices.humidifiers, async_add_entities, coordinator)


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: VeSyncDataCoordinator,
) -> None:
    """Add humidifier entities."""
    async_add_entities(
        VeSyncHumidifierHA(dev, coordinator)
        for dev in devices
        if is_humidifier(dev)
    )


def _get_ha_mode(vs_mode: str) -> str | None:
    ha_mode = VS_TO_HA_MODE_MAP.get(vs_mode)
    if ha_mode is None:
        _LOGGER.warning("Unknown mode '%s'", vs_mode)
    return ha_mode


class VeSyncHumidifierHA(VeSyncBaseEntity, HumidifierEntity):
    """Representation of a VeSync humidifier."""

    # The base VeSyncBaseEntity has _attr_has_entity_name and this is to follow the device name
    _attr_name = None

    _attr_supported_features = HumidifierEntityFeature.MODES
    _attr_device_class = HumidifierDeviceClass.HUMIDIFIER

    _attr_translation_key = "vesync"

    def __init__(
        self,
        device: VeSyncBaseDevice,
        coordinator: VeSyncDataCoordinator,
    ) -> None:
        """Initialize the VeSyncHumidifierHA device."""
        super().__init__(device, coordinator)

        # 2 Vesync humidifier modes (humidity and auto) maps to the HA mode auto.
        # They are on different devices though. We need to map HA mode to the
        # device specific mode when setting it.

        self._ha_to_vs_mode_map: dict[str, str] = {}
        self._available_modes: list[str] = []
        self._attr_max_humidity = max(device.target_minmax)
        self._attr_min_humidity = min(device.target_minmax)

        # Populate maps once.
        for vs_mode in self.device.mist_modes:
            ha_mode = _get_ha_mode(vs_mode)
            if ha_mode:
                self._available_modes.append(ha_mode)
                self._ha_to_vs_mode_map[ha_mode] = vs_mode

        self._available_modes.sort()

    def _get_vs_mode(self, ha_mode: str) -> str | None:
        return self._ha_to_vs_mode_map.get(ha_mode)

    @property
    def available_modes(self) -> list[str]:
        """Return the available mist modes."""
        return self._available_modes

    @property
    def action(self) -> HumidifierAction | None:
        """Return the current action."""
        if not self.is_on:
            return HumidifierAction.OFF

        if self.mode == MODE_NORMAL:
            return HumidifierAction.HUMIDIFYING

        if self.current_humidity < self.target_humidity:
            return HumidifierAction.HUMIDIFYING

        return HumidifierAction.IDLE

    @property
    def current_humidity(self) -> int:
        """Return the current humidity."""
        return self.device.state.humidity

    @property
    def target_humidity(self) -> int:
        """Return the humidity we try to reach."""
        target_humidity = getattr(self.device.state, "target_humidity", None)
        if target_humidity is None:
            target_humidity = getattr(self.device.state, "auto_humidity", None)
        # pyvesync should always provide at least one of these; fall back to min.
        return self._attr_min_humidity if target_humidity is None else target_humidity

    @property
    def mode(self) -> str | None:
        """Get the current preset mode."""
        return (
            None
            if self.device.state.mode is None
            else _get_ha_mode(self.device.state.mode)
        )

    async def async_set_humidity(self, humidity: int) -> None:
        """Set the target humidity of the device."""
        if not await self.device.set_humidity(humidity):
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()

    async def async_set_mode(self, mode: str) -> None:
        """Set the mode of the device."""
        if mode not in self.available_modes:
            raise HomeAssistantError(
                f"Invalid mode {mode}. Available modes: {self.available_modes}"
            )
        if not await self.device.set_mode(self._get_vs_mode(mode)):
            raise HomeAssistantError(self.device.last_response.message)

        if mode == MODE_SLEEP:
            # We successfully changed the mode. Consider it a success even if display operation fails.
            await self.device.toggle_display(False)

        # Changing mode while humidifier is off can implicitly turn it on; refresh to
        # ensure device status and related attributes are up to date.
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        success = await self.device.turn_on()
        if not success:
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        success = await self.device.turn_off()
        if not success:
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.device.state.device_status == "on"
