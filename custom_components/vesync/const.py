"""Constants for VeSync Component."""

DOMAIN = "vesync"
VS_DISCOVERY = "vesync_discovery_{}"
SERVICE_UPDATE_DEVS = "update_devices"

# Services (feature coverage helpers)
SERVICE_FRYER_COOK = "fryer_cook"
SERVICE_FRYER_SET_PREHEAT = "fryer_set_preheat"
SERVICE_FRYER_COOK_FROM_PREHEAT = "fryer_cook_from_preheat"

SERVICE_THERMOSTAT_CANCEL_HOLD = "thermostat_cancel_hold"
SERVICE_THERMOSTAT_SET_ECO_TYPE = "thermostat_set_eco_type"
SERVICE_THERMOSTAT_SET_LOCK = "thermostat_set_lock"

UPDATE_INTERVAL = 60
UPDATE_INTERVAL_ENERGY = 60 * 60 * 6
"""
Update interval for DataCoordinator.

The vesync daily quota formula is 3200 + 1500 * device_count.

An interval of 60 seconds amounts 1440 calls/day which
would be below the 4700 daily quota. For 2 devices, the
total would be 2880.

Using 30 seconds interval gives 8640 for 3 devices which
exceeds the quota of 7700.

Energy history is weekly/monthly/yearly and can be updated a lot more infrequently,
in this case every 6 hours.
"""
VS_DEVICES = "devices"
VS_COORDINATOR = "coordinator"
VS_COORDINATOR_ENERGY = "coordinator_energy"
VS_MANAGER = "manager"
VS_NUMBERS = "numbers"

VS_HUMIDIFIER_MODE_AUTO = "auto"
VS_HUMIDIFIER_MODE_HUMIDITY = "humidity"
VS_HUMIDIFIER_MODE_MANUAL = "manual"
VS_HUMIDIFIER_MODE_SLEEP = "sleep"

VS_FAN_MODE_AUTO = "auto"
VS_FAN_MODE_SLEEP = "sleep"
VS_FAN_MODE_ADVANCED_SLEEP = "advancedSleep"
VS_FAN_MODE_TURBO = "turbo"
VS_FAN_MODE_PET = "pet"
VS_FAN_MODE_MANUAL = "manual"
VS_FAN_MODE_NORMAL = "normal"

# not a full list as manual is used as speed not present
VS_FAN_MODE_PRESET_LIST_HA = [
    VS_FAN_MODE_AUTO,
    VS_FAN_MODE_SLEEP,
    VS_FAN_MODE_ADVANCED_SLEEP,
    VS_FAN_MODE_TURBO,
    VS_FAN_MODE_PET,
    VS_FAN_MODE_NORMAL,
]
NIGHT_LIGHT_LEVEL_BRIGHT = "bright"
NIGHT_LIGHT_LEVEL_DIM = "dim"
NIGHT_LIGHT_LEVEL_OFF = "off"

HUMIDIFIER_NIGHT_LIGHT_LEVEL_BRIGHT = "bright"
HUMIDIFIER_NIGHT_LIGHT_LEVEL_DIM = "dim"
HUMIDIFIER_NIGHT_LIGHT_LEVEL_OFF = "off"

OUTLET_NIGHT_LIGHT_LEVEL_AUTO = "auto"
OUTLET_NIGHT_LIGHT_LEVEL_OFF = "off"
OUTLET_NIGHT_LIGHT_LEVEL_ON = "on"

PURIFIER_NIGHT_LIGHT_LEVEL_DIM = "dim"
PURIFIER_NIGHT_LIGHT_LEVEL_OFF = "off"
PURIFIER_NIGHT_LIGHT_LEVEL_ON = "on"
