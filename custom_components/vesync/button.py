"""Support for VeSync buttons."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging

from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_fryer, iter_manager_devices
from .const import DOMAIN, VS_COORDINATOR, VS_DEVICES, VS_DISCOVERY, VS_MANAGER
from .coordinator import VeSyncDataCoordinator
from .entity import VeSyncBaseEntity

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class VeSyncButtonEntityDescription(ButtonEntityDescription):
    """Describe a VeSync button entity."""

    press_fn: Callable[[VeSyncBaseDevice], Awaitable[bool]]
    exists_fn: Callable[[VeSyncBaseDevice], bool] = lambda _: True


BUTTON_DESCRIPTIONS: tuple[VeSyncButtonEntityDescription, ...] = (
    VeSyncButtonEntityDescription(
        key="reset_filter",
        translation_key="reset_filter",
        entity_category=None,
        press_fn=lambda device: device.reset_filter(),
        exists_fn=lambda device: hasattr(device, "reset_filter"),
    ),
    VeSyncButtonEntityDescription(
        key="pause_cooking",
        translation_key="pause_cooking",
        press_fn=lambda device: device.pause(),
        exists_fn=lambda device: is_fryer(device) and hasattr(device, "pause"),
    ),
    VeSyncButtonEntityDescription(
        key="resume_cooking",
        translation_key="resume_cooking",
        press_fn=lambda device: device.resume(),
        exists_fn=lambda device: is_fryer(device) and hasattr(device, "resume"),
    ),
    VeSyncButtonEntityDescription(
        key="end_cooking",
        translation_key="end_cooking",
        press_fn=lambda device: device.end(),
        exists_fn=lambda device: is_fryer(device) and hasattr(device, "end"),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the VeSync button platform."""

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
    """Add button entities."""

    async_add_entities(
        VeSyncButtonEntity(dev, description, coordinator)
        for dev in devices
        for description in BUTTON_DESCRIPTIONS
        if description.exists_fn(dev)
    )


class VeSyncButtonEntity(VeSyncBaseEntity, ButtonEntity):
    """Representation of a VeSync button entity."""

    entity_description: VeSyncButtonEntityDescription

    def __init__(
        self,
        device: VeSyncBaseDevice,
        description: VeSyncButtonEntityDescription,
        coordinator: VeSyncDataCoordinator,
    ) -> None:
        """Initialize the VeSync button entity."""
        super().__init__(device, coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self.base_unique_id}-{description.key}"

    async def async_press(self) -> None:
        """Handle the button press."""
        if not await self.entity_description.press_fn(self.device):
            raise HomeAssistantError(self.device.last_response.message)

        await self.coordinator.async_request_refresh()
