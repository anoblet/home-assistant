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
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .common import is_fryer
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .entity import VeSyncBaseEntity
from .platform_setup import async_setup_vesync_platform_entry

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

    await async_setup_vesync_platform_entry(
        hass,
        config_entry,
        async_add_entities,
        _setup_entities,
    )


@callback
def _setup_entities(
    devices: list[VeSyncBaseDevice],
    async_add_entities: AddConfigEntryEntitiesCallback,
    coordinator: DataUpdateCoordinator,
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
        coordinator: DataUpdateCoordinator,
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
