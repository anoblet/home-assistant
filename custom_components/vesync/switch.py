"""Support for VeSync switches."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any, Final

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.switch import (
    SwitchDeviceClass,
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .common import is_fryer, is_outlet, is_wall_switch, iter_manager_devices, rgetattr
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


def _status_is_on(value: Any) -> bool:
    """Normalize VeSync status values to a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "on"
    return bool(value)


@dataclass(frozen=True, kw_only=True)
class VeSyncSwitchEntityDescription(SwitchEntityDescription):
    """A class that describes custom switch entities."""

    is_on: Callable[[VeSyncBaseDevice], bool]
    exists_fn: Callable[[VeSyncBaseDevice], bool]
    on_fn: Callable[[VeSyncBaseDevice], Awaitable[bool]]
    off_fn: Callable[[VeSyncBaseDevice], Awaitable[bool]]


async def _async_set_mute(device: VeSyncBaseDevice, value: bool) -> bool:
    """Set mute state."""
    if hasattr(device, "set_mute"):
        return await device.set_mute(value)
    if hasattr(device, "toggle_mute"):
        return await device.toggle_mute(value)
    return False


async def _async_set_auto_stop(device: VeSyncBaseDevice, value: bool) -> bool:
    """Set auto stop state."""
    if hasattr(device, "turn_on_auto_stop") and value:
        result = await device.turn_on_auto_stop()
        if not result and "request success" in str(device.last_response.message).lower():
            _LOGGER.debug(
                "VeSync reported request success for auto_stop turn_on despite false return"
            )
            return True
        return result
    if hasattr(device, "turn_off_auto_stop") and not value:
        result = await device.turn_off_auto_stop()
        if not result and "request success" in str(device.last_response.message).lower():
            _LOGGER.debug(
                "VeSync reported request success for auto_stop turn_off despite false return"
            )
            return True
        return result
    if hasattr(device, "toggle_automatic_stop"):
        result = await device.toggle_automatic_stop(value)
        if not result and "request success" in str(device.last_response.message).lower():
            _LOGGER.debug(
                "VeSync reported request success for auto_stop toggle despite false return"
            )
            return True
        return result
    return False


async def _async_set_light_detection(device: VeSyncBaseDevice, value: bool) -> bool:
    """Set light detection state (purifiers)."""
    if value and hasattr(device, "turn_on_light_detection"):
        return await device.turn_on_light_detection()
    if not value and hasattr(device, "turn_off_light_detection"):
        return await device.turn_off_light_detection()
    if hasattr(device, "toggle_light_detection"):
        return await device.toggle_light_detection(value)
    return False


async def _async_fryer_pause(device: VeSyncBaseDevice) -> bool:
    """Pause an air fryer cook session."""
    if hasattr(device, "pause"):
        return await device.pause()
    return False


async def _async_fryer_resume(device: VeSyncBaseDevice) -> bool:
    """Resume an air fryer cook session."""
    if hasattr(device, "resume"):
        return await device.resume()
    return False


SENSOR_DESCRIPTIONS: Final[tuple[VeSyncSwitchEntityDescription, ...]] = (
    VeSyncSwitchEntityDescription(
        key="device_status",
        is_on=lambda device: device.state.device_status == "on",
        # Other types of wall switches support dimming.  Those use light.py platform.
        exists_fn=lambda device: is_wall_switch(device) or is_outlet(device),
        translation_key="power",
        on_fn=lambda device: device.turn_on(),
        off_fn=lambda device: device.turn_off(),
    ),
    VeSyncSwitchEntityDescription(
        key="display",
        is_on=lambda device: device.state.display_set_status == "on",
        exists_fn=(
            lambda device: rgetattr(device, "state.display_set_status") is not None
        ),
        translation_key="display",
        on_fn=lambda device: device.toggle_display(True),
        off_fn=lambda device: device.toggle_display(False),
    ),
    VeSyncSwitchEntityDescription(
        key="displaying_type",
        is_on=lambda device: _status_is_on(rgetattr(device, "state.displaying_type")),
        exists_fn=lambda device: rgetattr(device, "state.displaying_type") is not None
        and callable(getattr(device, "toggle_displaying_type", None)),
        translation_key="displaying_type",
        on_fn=lambda device: device.toggle_displaying_type(True),
        off_fn=lambda device: device.toggle_displaying_type(False),
    ),
    VeSyncSwitchEntityDescription(
        key="indicator_light",
        is_on=lambda device: _status_is_on(rgetattr(device, "state.indicator_status")),
        exists_fn=lambda device: bool(getattr(device, "supports_indicator_light", False))
        and callable(getattr(device, "toggle_indicator_light", None)),
        translation_key="indicator_light",
        on_fn=lambda device: device.toggle_indicator_light(True),
        off_fn=lambda device: device.toggle_indicator_light(False),
    ),
    VeSyncSwitchEntityDescription(
        key="backlight",
        is_on=lambda device: _status_is_on(rgetattr(device, "state.backlight_status")),
        exists_fn=lambda device: bool(getattr(device, "supports_backlight", False))
        and callable(getattr(device, "set_backlight_status", None)),
        translation_key="backlight",
        on_fn=lambda device: device.set_backlight_status(True),
        off_fn=lambda device: device.set_backlight_status(False),
    ),
    VeSyncSwitchEntityDescription(
        key="child_lock",
        is_on=lambda device: device.state.child_lock,
        exists_fn=lambda device: rgetattr(device, "state.child_lock") is not None
        and callable(getattr(device, "toggle_child_lock", None)),
        translation_key="child_lock",
        on_fn=lambda device: device.toggle_child_lock(True),
        off_fn=lambda device: device.toggle_child_lock(False),
    ),
    VeSyncSwitchEntityDescription(
        key="light_detection",
        is_on=lambda device: rgetattr(device, "state.light_detection_switch") == "on",
        exists_fn=lambda device: bool(getattr(device, "supports_light_detection", False)),
        translation_key="light_detection",
        on_fn=lambda device: _async_set_light_detection(device, True),
        off_fn=lambda device: _async_set_light_detection(device, False),
    ),
    VeSyncSwitchEntityDescription(
        key="cooking_status",
        is_on=lambda device: bool(rgetattr(device, "state.is_running")),
        exists_fn=lambda device: is_fryer(device)
        and hasattr(device, "pause")
        and hasattr(device, "resume"),
        translation_key="cooking_status",
        on_fn=lambda device: _async_fryer_resume(device),
        off_fn=lambda device: _async_fryer_pause(device),
    ),
    VeSyncSwitchEntityDescription(
        key="vertical_oscillation",
        is_on=lambda device: rgetattr(device, "state.vertical_oscillation_status") == "on",
        exists_fn=lambda device: bool(getattr(device, "supports_vertical_oscillation", False)) and hasattr(device, "turn_on_vertical_oscillation"),
        translation_key="vertical_oscillation",
        on_fn=lambda device: device.turn_on_vertical_oscillation(),
        off_fn=lambda device: device.turn_off_vertical_oscillation(),
    ),
    VeSyncSwitchEntityDescription(
        key="horizontal_oscillation",
        is_on=lambda device: rgetattr(device, "state.horizontal_oscillation_status") == "on",
        exists_fn=lambda device: bool(getattr(device, "supports_horizontal_oscillation", False)) and hasattr(device, "turn_on_horizontal_oscillation"),
        translation_key="horizontal_oscillation",
        on_fn=lambda device: device.turn_on_horizontal_oscillation(),
        off_fn=lambda device: device.turn_off_horizontal_oscillation(),
    ),
    VeSyncSwitchEntityDescription(
        key="drying_mode",
        is_on=lambda device: bool(rgetattr(device, "state.drying_mode_enabled")),
        exists_fn=lambda device: hasattr(device, "turn_on_drying_mode"),
        translation_key="drying_mode",
        on_fn=lambda device: device.turn_on_drying_mode(),
        off_fn=lambda device: device.turn_off_drying_mode(),
    ),
    VeSyncSwitchEntityDescription(
        key="mute",
        name="Mute",
        exists_fn=lambda device: hasattr(device, "set_mute")
        or hasattr(device, "toggle_mute"),
        translation_key="mute",
        on_fn=lambda device: _async_set_mute(device, True),
        off_fn=lambda device: _async_set_mute(device, False),
    ),
    VeSyncSwitchEntityDescription(
        key="auto_stop",
        is_on=lambda device: bool(rgetattr(device, "state.automatic_stop")),
        exists_fn=lambda device: hasattr(device, "turn_on_auto_stop")
        or hasattr(device, "toggle_automatic_stop"),
        translation_key="auto_stop",
        on_fn=lambda device: _async_set_auto_stop(device, True),
        off_fn=lambda device: _async_set_auto_stop(device, False),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up switch platform."""

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
    """Check if device is online and add entity."""
    async_add_entities(
        VeSyncSwitchEntity(dev, description, coordinator)
        for dev in devices
        for description in SENSOR_DESCRIPTIONS
        if description.exists_fn(dev)
    )


class VeSyncSwitchEntity(SwitchEntity, VeSyncBaseEntity):
    """VeSync switch entity class."""

    entity_description: VeSyncSwitchEntityDescription

    def __init__(
        self,
        device: VeSyncBaseDevice,
        description: VeSyncSwitchEntityDescription,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.base_unique_id}-{description.key}"
        if is_outlet(self.device):
            self._attr_device_class = SwitchDeviceClass.OUTLET
        elif is_wall_switch(self.device):
            self._attr_device_class = SwitchDeviceClass.SWITCH

    @property
    def is_on(self) -> bool | None:
        """Return the entity value to represent the entity state."""
        return self.entity_description.is_on(self.device)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if not await self.entity_description.off_fn(self.device):
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if not await self.entity_description.on_fn(self.device):
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()
