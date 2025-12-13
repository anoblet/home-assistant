"""Diagnostics support for VeSync."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {CONF_PASSWORD, CONF_USERNAME}

async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    manager = data["manager"]

    device_data = {
        "fans": [d.__dict__ for d in getattr(manager, "fans", [])],
        "outlets": [d.__dict__ for d in getattr(manager, "outlets", [])],
        "switches": [d.__dict__ for d in getattr(manager, "switches", [])],
        "bulbs": [d.__dict__ for d in getattr(manager, "bulbs", [])],
        "kitchen": [d.__dict__ for d in getattr(manager, "kitchen", [])],
        "thermostats": [d.__dict__ for d in getattr(manager, "thermostats", [])],
    }

    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "devices": async_redact_data(device_data, TO_REDACT),
    }
