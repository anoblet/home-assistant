"""Common utilities for VeSync Component."""
from .const import VS_AIRFRYER, VS_THERMOSTAT

async def async_get_config_id(config_entry):
    """Return the config ID for the entry."""
    return config_entry.entry_id

def is_air_fryer(device_type):
    """Return true if the device is an air fryer."""
    return device_type.lower() in ["vesyncairfryer158"]

def is_thermostat(device_type):
    """Return true if the device is a thermostat."""
    return device_type.lower() in ["vesyncaurathermostat"]

def is_fan(device_type):
    """Return true if the device is a fan."""
    return "purifier" in device_type.lower() or device_type.lower() in ["lv-pur131s", "lv-pur131s-rx", "lv-h132s", "lv-h133s"]

def is_humidifier(device_type):
    """Return true if the device is a humidifier."""
    return "humidifier" in device_type.lower() or "luh-a602s-wus" in device_type.lower()
