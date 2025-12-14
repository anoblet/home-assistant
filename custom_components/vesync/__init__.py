"""VeSync integration."""

import re
import logging

from pyvesync import VeSync
from pyvesync.utils.errors import VeSyncLoginError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import DeviceEntry
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util import slugify

from .const import (
    DOMAIN,
    SERVICE_UPDATE_DEVS,
    VS_COORDINATOR,
    VS_DEVICES,
    VS_DISCOVERY,
    VS_MANAGER,
)
from .coordinator import VeSyncDataCoordinator

PLATFORMS = [
    Platform.BUTTON,
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
    Platform.FAN,
    Platform.HUMIDIFIER,
    Platform.LIGHT,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.UPDATE,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Vesync as config entry."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    time_zone = str(hass.config.time_zone)

    manager = VeSync(
        username=username,
        password=password,
        time_zone=time_zone,
        session=async_get_clientsession(hass),
    )
    try:
        await manager.login()
    except VeSyncLoginError as err:
        raise ConfigEntryAuthFailed from err

    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][VS_MANAGER] = manager

    coordinator = VeSyncDataCoordinator(hass, config_entry, manager)

    # Store coordinator at domain level since only single integration instance is permitted.
    hass.data[DOMAIN][VS_COORDINATOR] = coordinator
    await manager.update()
    await manager.check_firmware()

    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    async def async_new_device_discovery(service: ServiceCall) -> None:
        """Discover and add new devices."""
        manager = hass.data[DOMAIN][VS_MANAGER]
        known_devices = list(manager.devices)
        await manager.get_devices()
        new_devices = [
            device for device in manager.devices if device not in known_devices
        ]

        if new_devices:
            _LOGGER.debug("Discovered %s new VeSync devices", len(new_devices))
            async_dispatcher_send(
                hass,
                VS_DISCOVERY.format(VS_DEVICES),
                new_devices,
            )

    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_DEVS, async_new_device_discovery
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data.pop(DOMAIN)

    return unload_ok


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating VeSync config entry: %s minor version: %s",
        config_entry.version,
        config_entry.minor_version,
    )

    minor_version = config_entry.minor_version

    if minor_version < 2:
        # Migrate switch/outlets entity to a new unique ID
        _LOGGER.debug("Migrating VeSync config entry from version 1 to version 2")
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )
        for reg_entry in registry_entries:
            if "-" not in reg_entry.unique_id and reg_entry.entity_id.startswith(
                Platform.SWITCH
            ):
                _LOGGER.debug(
                    "Migrating switch/outlet entity from unique_id: %s to unique_id: %s",
                    reg_entry.unique_id,
                    reg_entry.unique_id + "-device_status",
                )
                entity_registry.async_update_entity(
                    reg_entry.entity_id,
                    new_unique_id=reg_entry.unique_id + "-device_status",
                )
            else:
                _LOGGER.debug("Skipping entity with unique_id: %s", reg_entry.unique_id)
        hass.config_entries.async_update_entry(config_entry, minor_version=2)
        minor_version = 2

    if minor_version < 3:
        # Fix legacy entities that were created with a None name and thus got an `_none` suffix.
        _LOGGER.debug("Migrating VeSync config entry from version 2 to version 3")
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )

        for reg_entry in registry_entries:
            if not (
                reg_entry.entity_id.startswith("switch.")
                and reg_entry.entity_id.endswith("_none")
                and reg_entry.unique_id.endswith("-device_status")
            ):
                continue

            new_entity_id = reg_entry.entity_id[: -len("_none")] + "_power"
            _LOGGER.debug(
                "Migrating legacy VeSync switch entity_id from %s to %s",
                reg_entry.entity_id,
                new_entity_id,
            )

            # If the target entity_id is already taken, remove the legacy entry so HA can
            # recreate it with the correct entity_id from translations.
            if getattr(entity_registry, "async_get", None) and entity_registry.async_get(
                new_entity_id
            ):
                _LOGGER.debug(
                    "Target entity_id %s already exists; removing legacy entity_id %s",
                    new_entity_id,
                    reg_entry.entity_id,
                )
                entity_registry.async_remove(reg_entry.entity_id)
                continue

            try:
                entity_registry.async_update_entity(
                    reg_entry.entity_id, new_entity_id=new_entity_id
                )
            except TypeError:
                _LOGGER.debug(
                    "Entity registry does not support renaming entity_id; removing legacy %s",
                    reg_entry.entity_id,
                )
                entity_registry.async_remove(reg_entry.entity_id)

        hass.config_entries.async_update_entry(config_entry, minor_version=3)
        minor_version = 3

    if minor_version < 4:
        # Rename any remaining entities created with a None name and thus got an `_none` suffix.
        # This is broader than the v2->v3 migration which only targeted the legacy device_status switch.
        _LOGGER.debug("Migrating VeSync config entry from version 3 to version 4")
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )

        for reg_entry in registry_entries:
            if not reg_entry.entity_id.endswith("_none"):
                continue

            # Derive a stable suffix from the unique_id. Our entities use
            # "<device_base_unique_id>-<description.key>".
            unique_suffix = None
            if reg_entry.unique_id and "-" in reg_entry.unique_id:
                unique_suffix = reg_entry.unique_id.rsplit("-", 1)[-1]

            if not unique_suffix:
                _LOGGER.debug(
                    "Skipping legacy _none entity with unexpected unique_id: %s",
                    reg_entry.unique_id,
                )
                continue

            # Special-case the legacy device status switch which should now be called "power".
            object_suffix = "power" if unique_suffix == "device_status" else unique_suffix

            new_entity_id = (
                reg_entry.entity_id[: -len("_none")] + f"_{slugify(object_suffix)}"
            )

            _LOGGER.debug(
                "Migrating legacy VeSync entity_id from %s to %s",
                reg_entry.entity_id,
                new_entity_id,
            )

            # If the target entity_id is already taken, remove the legacy entry so HA can
            # recreate it with the correct entity_id.
            if getattr(entity_registry, "async_get", None) and entity_registry.async_get(
                new_entity_id
            ):
                _LOGGER.debug(
                    "Target entity_id %s already exists; removing legacy entity_id %s",
                    new_entity_id,
                    reg_entry.entity_id,
                )
                entity_registry.async_remove(reg_entry.entity_id)
                continue

            try:
                entity_registry.async_update_entity(
                    reg_entry.entity_id, new_entity_id=new_entity_id
                )
            except TypeError:
                _LOGGER.debug(
                    "Entity registry does not support renaming entity_id; removing legacy %s",
                    reg_entry.entity_id,
                )
                entity_registry.async_remove(reg_entry.entity_id)

        hass.config_entries.async_update_entry(config_entry, minor_version=4)
        minor_version = 4

    if minor_version < 5:
        # Some HA versions/registry backends can silently ignore entity_id renames during
        # migration. As a safety net, verify the rename took effect; otherwise remove the
        # legacy entry so it will be recreated with the correct entity_id.
        _LOGGER.debug("Migrating VeSync config entry from version 4 to version 5")
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )

        for reg_entry in registry_entries:
            if not reg_entry.entity_id.endswith("_none"):
                continue

            unique_suffix = None
            if reg_entry.unique_id and "-" in reg_entry.unique_id:
                unique_suffix = reg_entry.unique_id.rsplit("-", 1)[-1]

            object_suffix = (
                "power" if unique_suffix == "device_status" else (unique_suffix or "")
            )

            new_entity_id = None
            if object_suffix:
                new_entity_id = (
                    reg_entry.entity_id[: -len("_none")] + f"_{slugify(object_suffix)}"
                )

            if new_entity_id:
                _LOGGER.debug(
                    "Attempting to migrate legacy VeSync entity_id from %s to %s",
                    reg_entry.entity_id,
                    new_entity_id,
                )
                try:
                    entity_registry.async_update_entity(
                        reg_entry.entity_id, new_entity_id=new_entity_id
                    )
                except TypeError:
                    # Renaming not supported; fall back to removal below.
                    pass

                # Verify the rename actually happened; otherwise remove the legacy entry.
                if getattr(entity_registry, "async_get", None) and entity_registry.async_get(
                    new_entity_id
                ):
                    continue

            _LOGGER.debug(
                "Removing legacy VeSync entity_id %s to eliminate _none suffix",
                reg_entry.entity_id,
            )
            entity_registry.async_remove(reg_entry.entity_id)

        hass.config_entries.async_update_entry(config_entry, minor_version=5)
        minor_version = 5

    if minor_version < 6:
        # Clean up any remaining `_none_*` entity ids (e.g. `_none_2`, `_none_3`).
        _LOGGER.debug("Migrating VeSync config entry from version 5 to version 6")
        entity_registry = er.async_get(hass)
        registry_entries = er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )

        for reg_entry in registry_entries:
            if "_none" not in reg_entry.entity_id:
                continue

            # Only rewrite object_ids that actually end with `_none` or `_none_<n>`.
            try:
                domain, object_id = reg_entry.entity_id.split(".", 1)
            except ValueError:
                continue

            device_object_id = re.sub(r"_none(?:_\d+)?$", "", object_id)
            if device_object_id == object_id:
                continue

            unique_suffix = None
            if reg_entry.unique_id and "-" in reg_entry.unique_id:
                unique_suffix = reg_entry.unique_id.rsplit("-", 1)[-1]

            if not unique_suffix:
                _LOGGER.debug(
                    "Removing legacy VeSync entity_id %s (unable to derive suffix)",
                    reg_entry.entity_id,
                )
                entity_registry.async_remove(reg_entry.entity_id)
                continue

            object_suffix = "power" if unique_suffix == "device_status" else unique_suffix
            new_entity_id = f"{domain}.{device_object_id}_{slugify(object_suffix)}"

            _LOGGER.debug(
                "Attempting to migrate legacy VeSync entity_id from %s to %s",
                reg_entry.entity_id,
                new_entity_id,
            )

            # If the target exists already, remove the legacy one.
            if getattr(entity_registry, "async_get", None) and entity_registry.async_get(
                new_entity_id
            ):
                entity_registry.async_remove(reg_entry.entity_id)
                continue

            try:
                entity_registry.async_update_entity(
                    reg_entry.entity_id, new_entity_id=new_entity_id
                )
            except TypeError:
                # Renaming not supported; fall back to removal.
                entity_registry.async_remove(reg_entry.entity_id)
                continue

            # Verify rename applied; otherwise remove so it gets recreated correctly.
            if getattr(entity_registry, "async_get", None) and entity_registry.async_get(
                new_entity_id
            ):
                continue

            entity_registry.async_remove(reg_entry.entity_id)

        hass.config_entries.async_update_entry(config_entry, minor_version=6)
        minor_version = 6

    return True


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    manager = hass.data[DOMAIN][VS_MANAGER]
    await manager.get_devices()
    for dev in manager.devices:
        if isinstance(dev.sub_device_no, int):
            device_id = f"{dev.cid}{dev.sub_device_no!s}"
        else:
            device_id = dev.cid
        identifier = next(iter(device_entry.identifiers), None)
        if identifier and device_id == identifier[1]:
            return False

    return True
