"""The VeSync integration."""
import logging

from pyvesync import VeSync

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, VS_DISCOVERY, VS_SWITCH, VS_FAN, VS_LIGHT, VS_SENSOR, VS_HUMIDIFIER, VS_NUMBER, VS_BINARY_SENSOR, VS_BUTTON, VS_CLIMATE, VS_SELECT
from .coordinator import VeSyncDataCoordinator
from .common import async_get_config_id

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [
    Platform.SWITCH,
    Platform.FAN,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.HUMIDIFIER,
    Platform.NUMBER,
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SELECT,
    Platform.UPDATE,
]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up VeSync from a config entry."""
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    manager = VeSync(username, password)

    try:
        login = await manager.login()
    except Exception as err:
        raise ConfigEntryNotReady from err

    if not login:
        _LOGGER.error("Unable to login to VeSync")
        return False

    coordinator = VeSyncDataCoordinator(hass, manager)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "manager": manager,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
