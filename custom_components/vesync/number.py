"""Support for VeSync numeric entities."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_fan, is_humidifier, iter_manager_devices
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


def _get_warm_mist_level(device: VeSyncBaseDevice) -> float:
    """Get warm mist level for humidifiers.

    pyvesync exposes warm mist level on the humidifier state as
    `state.warm_mist_level` (int | None).
    """
    value = getattr(getattr(device, "state", None), "warm_mist_level", None)
    return 0.0 if value is None else float(value)


def _supports_warm_mist(device: VeSyncBaseDevice) -> bool:
    """Return True if the humidifier supports warm mist."""
    if not is_humidifier(device):
        return False

    # Prefer explicit capability if present.
    if bool(getattr(device, "supports_warm_mist", False)):
        return True

    # Fall back to the presence of the state attribute or setters.
    if getattr(getattr(device, "state", None), "warm_mist_level", None) is not None:
        return True

    return hasattr(device, "set_warm_level") or hasattr(device, "set_warm_mist")


async def _async_set_warm_mist_level(device: VeSyncBaseDevice, value: float) -> bool:
    """Set warm mist level for humidifiers.

    pyvesync==3.3.3 exposes `set_warm_level`; older/newer versions may expose
    `set_warm_mist`.
    """
    warm_level = int(value)
    if hasattr(device, "set_warm_level"):
        return await device.set_warm_level(warm_level)
    if hasattr(device, "set_warm_mist"):
        return await device.set_warm_mist(warm_level)
    return False


def _get_timer_duration(device: VeSyncBaseDevice) -> float:
    """Get timer value in minutes.

    pyvesync==3.3.3 stores timers on `device.state.timer` and the Timer object
    exposes `time_remaining` and `timer_duration` (older variants may use
    `duration` or dict-like structures).

    Prefer remaining time when available.
    """

    timer = getattr(getattr(device, "state", None), "timer", None)
    if timer is None:
        timer = getattr(device, "timer", None)

    if timer is None:
        return 0.0

    if isinstance(timer, dict):
        if "time_remaining" in timer:
            return float(timer.get("time_remaining", 0) or 0)
        if "remaining" in timer:
            return float(timer.get("remaining", 0) or 0)
        if "timer_duration" in timer:
            return float(timer.get("timer_duration", 0) or 0)
        return float(timer.get("duration", 0) or 0)

    for attr in ("time_remaining", "remaining", "timer_duration", "duration"):
        value = getattr(timer, attr, None)
        if value is not None:
            return float(value)

    return 0.0


async def _set_timer_duration(device: VeSyncBaseDevice, value: float) -> bool:
    """Set timer duration."""
    minutes = int(value)
    if minutes == 0:
        if hasattr(device, "clear_timer"):
            return await device.clear_timer()
        return False

    if hasattr(device, "set_timer"):
        # pyvesync==3.3.3: set_timer(duration: int, action: str | None = None)
        return await device.set_timer(minutes)
    return False


@dataclass(frozen=True, kw_only=True)
class VeSyncNumberEntityDescription(NumberEntityDescription):
    """Class to describe a Vesync number entity."""

    exists_fn: Callable[[VeSyncBaseDevice], bool] = lambda _: True
    value_fn: Callable[[VeSyncBaseDevice], float]
    native_min_value_fn: Callable[[VeSyncBaseDevice], float]
    native_max_value_fn: Callable[[VeSyncBaseDevice], float]
    set_value_fn: Callable[[VeSyncBaseDevice, float], Awaitable[bool]]


NUMBER_DESCRIPTIONS: list[VeSyncNumberEntityDescription] = [
    VeSyncNumberEntityDescription(
        key="mist_level",
        name="Mist level",
        translation_key="mist_level",
        native_min_value_fn=lambda device: min(device.mist_levels),
        native_max_value_fn=lambda device: max(device.mist_levels),
        native_step=1,
        mode=NumberMode.SLIDER,
        exists_fn=is_humidifier,
        set_value_fn=lambda device, value: device.set_mist_level(value),
        value_fn=lambda device: device.state.mist_virtual_level,
    ),
    VeSyncNumberEntityDescription(
        key="warm_mist_level",
        name="Warm mist level",
        translation_key="warm_mist_level",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 3,
        native_step=1,
        mode=NumberMode.SLIDER,
        exists_fn=_supports_warm_mist,
        set_value_fn=_async_set_warm_mist_level,
        value_fn=_get_warm_mist_level,
    ),
    VeSyncNumberEntityDescription(
        key="timer",
        name="Timer",
        translation_key="timer",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 1440,
        native_step=1,
        mode=NumberMode.BOX,
        exists_fn=lambda device: hasattr(device, "set_timer")
        and hasattr(device, "clear_timer"),
        set_value_fn=_set_timer_duration,
        value_fn=_get_timer_duration,
    ),
    VeSyncNumberEntityDescription(
        key="horizontal_oscillation_left",
        name="Horizontal oscillation left",
        translation_key="horizontal_oscillation_left",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 360,
        native_step=1,
        mode=NumberMode.BOX,
        exists_fn=lambda device: is_fan(device)
        and bool(getattr(device, "supports_set_oscillation_range", False))
        and hasattr(device, "set_horizontal_oscillation_range"),
        set_value_fn=lambda device, value: device.set_horizontal_oscillation_range(
            left=int(value),
            right=int(getattr(getattr(device.state, "oscillation_range", None), "right", 0) or 0),
        ),
        value_fn=lambda device: float(
            getattr(getattr(device.state, "oscillation_range", None), "left", 0) or 0
        ),
    ),
    VeSyncNumberEntityDescription(
        key="horizontal_oscillation_right",
        name="Horizontal oscillation right",
        translation_key="horizontal_oscillation_right",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 360,
        native_step=1,
        mode=NumberMode.BOX,
        exists_fn=lambda device: is_fan(device)
        and bool(getattr(device, "supports_set_oscillation_range", False))
        and hasattr(device, "set_horizontal_oscillation_range"),
        set_value_fn=lambda device, value: device.set_horizontal_oscillation_range(
            left=int(getattr(getattr(device.state, "oscillation_range", None), "left", 0) or 0),
            right=int(value),
        ),
        value_fn=lambda device: float(
            getattr(getattr(device.state, "oscillation_range", None), "right", 0) or 0
        ),
    ),
    VeSyncNumberEntityDescription(
        key="vertical_oscillation_top",
        name="Vertical oscillation top",
        translation_key="vertical_oscillation_top",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 360,
        native_step=1,
        mode=NumberMode.BOX,
        exists_fn=lambda device: is_fan(device)
        and bool(getattr(device, "supports_set_oscillation_range", False))
        and hasattr(device, "set_vertical_oscillation_range"),
        set_value_fn=lambda device, value: device.set_vertical_oscillation_range(
            top=int(value),
            bottom=int(getattr(getattr(device.state, "oscillation_range", None), "bottom", 0) or 0),
        ),
        value_fn=lambda device: float(
            getattr(getattr(device.state, "oscillation_range", None), "top", 0) or 0
        ),
    ),
    VeSyncNumberEntityDescription(
        key="vertical_oscillation_bottom",
        name="Vertical oscillation bottom",
        translation_key="vertical_oscillation_bottom",
        native_min_value_fn=lambda device: 0,
        native_max_value_fn=lambda device: 360,
        native_step=1,
        mode=NumberMode.BOX,
        exists_fn=lambda device: is_fan(device)
        and bool(getattr(device, "supports_set_oscillation_range", False))
        and hasattr(device, "set_vertical_oscillation_range"),
        set_value_fn=lambda device, value: device.set_vertical_oscillation_range(
            top=int(getattr(getattr(device.state, "oscillation_range", None), "top", 0) or 0),
            bottom=int(value),
        ),
        value_fn=lambda device: float(
            getattr(getattr(device.state, "oscillation_range", None), "bottom", 0) or 0
        ),
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities."""

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
    """Add number entities."""

    async_add_entities(
        VeSyncNumberEntity(dev, description, coordinator)
        for dev in devices
        for description in NUMBER_DESCRIPTIONS
        if description.exists_fn(dev)
    )


class VeSyncNumberEntity(VeSyncBaseEntity, NumberEntity):
    """A class to set numeric options on Vesync device."""

    entity_description: VeSyncNumberEntityDescription

    def __init__(
        self,
        device: VeSyncBaseDevice,
        description: VeSyncNumberEntityDescription,
        coordinator: VeSyncDataCoordinator,
    ) -> None:
        """Initialize the VeSync number device."""
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{super().unique_id}-{description.key}"

    @property
    def native_value(self) -> float:
        """Return the value reported by the number."""
        return self.entity_description.value_fn(self.device)

    @property
    def native_min_value(self) -> float:
        """Return the value reported by the number."""
        return self.entity_description.native_min_value_fn(self.device)

    @property
    def native_max_value(self) -> float:
        """Return the value reported by the number."""
        return self.entity_description.native_max_value_fn(self.device)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        if not await self.entity_description.set_value_fn(self.device, value):
            raise HomeAssistantError(self.device.last_response.message)
        await self.coordinator.async_request_refresh()
