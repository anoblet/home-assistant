"""Support for VeSync bulbs and wall dimmers."""

import logging
from typing import Any

from pyvesync.base_devices.bulb_base import VeSyncBulb
from pyvesync.base_devices.switch_base import VeSyncSwitch
from pyvesync.base_devices.vesyncbasedevice import VeSyncBaseDevice

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import color as color_util

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from .entity import VeSyncBaseEntity
from .platform_setup import async_setup_vesync_platform_entry

_LOGGER = logging.getLogger(__name__)
MAX_MIREDS = 370  # 1,000,000 divided by 2700 Kelvin = 370 Mireds
MIN_MIREDS = 153  # 1,000,000 divided by 6500 Kelvin = 153 Mireds


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up lights."""

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
    """Check if device is a light and add entity."""
    entities: list[VeSyncBaseEntity] = []
    for dev in devices:
        if isinstance(dev, VeSyncBulb):
            if getattr(dev, "rgb_supported", False) or hasattr(dev, "set_hsv") or hasattr(
                dev, "set_rgb"
            ):
                entities.append(VeSyncColorLightHA(dev, coordinator))
            elif dev.supports_color_temp:
                entities.append(VeSyncTunableWhiteLightHA(dev, coordinator))
            elif dev.supports_brightness:
                entities.append(VeSyncDimmableLightHA(dev, coordinator))
        elif isinstance(dev, VeSyncSwitch):
            # Wall switches and dimmer switches may expose multiple light-like controls.
            if dev.supports_dimmable:
                entities.append(VeSyncDimmableLightHA(dev, coordinator))
            if getattr(dev, "supports_backlight_color", False):
                entities.append(VeSyncBacklightLightHA(dev, coordinator))

    async_add_entities(entities, update_before_add=True)


def _status_is_on(value: Any) -> bool:
    """Normalize VeSync status values to a boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "on"
    return bool(value)


class VeSyncBaseLightHA(VeSyncBaseEntity, LightEntity):
    """Base class for VeSync Light Devices Representations."""

    _attr_name = None

    @property
    def is_on(self) -> bool:
        """Return True if device is on."""
        return self.device.state.device_status == "on"

    @property
    def brightness(self) -> int:
        """Get light brightness."""
        # get value from pyvesync library api,
        result = self.device.state.brightness
        try:
            # check for validity of brightness value received
            brightness_value = int(result)
        except ValueError:
            # deal if any unexpected/non numeric value
            _LOGGER.debug(
                "VeSync - received unexpected 'brightness' value from pyvesync api: %s",
                result,
            )
            return 0
        # convert percent brightness to ha expected range
        return round((max(1, brightness_value) / 100) * 255)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        attribute_adjustment_only = False
        # set white temperature
        if self.color_mode == ColorMode.COLOR_TEMP and ATTR_COLOR_TEMP_KELVIN in kwargs:
            # get white temperature from HA data
            color_temp = color_util.color_temperature_kelvin_to_mired(
                kwargs[ATTR_COLOR_TEMP_KELVIN]
            )
            # ensure value between min-max supported Mireds
            color_temp = max(MIN_MIREDS, min(color_temp, MAX_MIREDS))
            # convert Mireds to Percent value that api expects
            color_temp = round(
                ((color_temp - MIN_MIREDS) / (MAX_MIREDS - MIN_MIREDS)) * 100
            )
            # flip cold/warm to what pyvesync api expects
            color_temp = 100 - color_temp
            # ensure value between 0-100
            color_temp = max(0, min(color_temp, 100))
            # call pyvesync library api method to set color_temp
            await self.device.set_color_temp(color_temp)
            # flag attribute_adjustment_only, so it doesn't turn_on the device redundantly
            attribute_adjustment_only = True
        # set brightness level
        if (
            self.color_mode in (ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP)
            and ATTR_BRIGHTNESS in kwargs
        ):
            # get brightness from HA data
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            # ensure value between 1-255
            brightness = max(1, min(brightness, 255))
            # convert to percent that vesync api expects
            brightness = round((brightness / 255) * 100)
            # ensure value between 1-100
            brightness = max(1, min(brightness, 100))
            # call pyvesync library api method to set brightness
            await self.device.set_brightness(brightness)
            # flag attribute_adjustment_only, so it doesn't
            # turn_on the device redundantly
            attribute_adjustment_only = True
        # check flag if should skip sending the turn_on command
        if attribute_adjustment_only:
            await self.coordinator.async_request_refresh()
            return
        # send turn_on command to pyvesync api
        await self.device.turn_on()
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the device off."""
        await self.device.turn_off()
        await self.coordinator.async_request_refresh()


class VeSyncDimmableLightHA(VeSyncBaseLightHA, LightEntity):
    """Representation of a VeSync dimmable light device."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}


class VeSyncTunableWhiteLightHA(VeSyncBaseLightHA, LightEntity):
    """Representation of a VeSync Tunable White Light device."""

    _attr_color_mode = ColorMode.COLOR_TEMP
    _attr_min_color_temp_kelvin = 2700  # 370 Mireds
    _attr_max_color_temp_kelvin = 6500  # 153 Mireds
    _attr_supported_color_modes = {ColorMode.COLOR_TEMP}

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the color temperature value in Kelvin."""
        # get value from pyvesync library api
        # pyvesync v3 provides BulbState.color_temp_kelvin() - possible to use that instead?
        result = self.device.state.color_temp
        try:
            # check for validity of brightness value received
            color_temp_value = int(result)
        except ValueError:
            # deal if any unexpected/non numeric value
            _LOGGER.debug(
                (
                    "VeSync - received unexpected 'color_temp_pct' value from pyvesync"
                    " api: %s"
                ),
                result,
            )
            return None
        # flip cold/warm
        color_temp_value = 100 - color_temp_value
        # ensure value between 0-100
        color_temp_value = max(0, min(color_temp_value, 100))
        # convert percent value to Mireds
        color_temp_value = round(
            MIN_MIREDS + ((MAX_MIREDS - MIN_MIREDS) / 100 * color_temp_value)
        )
        # ensure value between minimum and maximum Mireds
        return color_util.color_temperature_mired_to_kelvin(
            max(MIN_MIREDS, min(color_temp_value, MAX_MIREDS))
        )


class VeSyncColorLightHA(VeSyncTunableWhiteLightHA):
    """Representation of a VeSync Color Light device."""

    _attr_supported_color_modes = {ColorMode.COLOR_TEMP, ColorMode.HS}

    @property
    def color_mode(self) -> ColorMode:
        """Return the color mode of the light."""
        # Check if in color mode
        if getattr(self.device.state, "color_mode", None) == "color":
            return ColorMode.HS
        return ColorMode.COLOR_TEMP

    @property
    def hs_color(self) -> tuple[float, float] | None:
        """Return the hs color value."""
        if getattr(self.device.state, "color_mode", None) == "color":
            # pyvesync usually stores hue/saturation in state
            hue = getattr(self.device.state, "hue", None)
            saturation = getattr(self.device.state, "saturation", None)
            if hue is not None and saturation is not None:
                return (float(hue), float(saturation))
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the device on."""
        # Handle HS Color
        if ATTR_HS_COLOR in kwargs:
            hs_color = kwargs[ATTR_HS_COLOR]
            hue = int(hs_color[0])
            saturation = int(hs_color[1])

            brightness = kwargs.get(ATTR_BRIGHTNESS)
            if brightness is None:
                brightness = self.brightness or 255

            # Convert brightness to 0-100
            brightness_pct = round((brightness / 255) * 100)
            brightness_pct = max(1, min(brightness_pct, 100))

            # pyvesync==3.3.3 exposes set_hsv / set_rgb (no set_color).
            if hasattr(self.device, "set_hsv"):
                await self.device.set_hsv(float(hue), float(saturation), float(brightness_pct))
            else:
                red, green, blue = color_util.color_hs_to_RGB(hue, saturation)
                if hasattr(self.device, "set_rgb"):
                    await self.device.set_rgb(float(red), float(green), float(blue))
                    if ATTR_BRIGHTNESS in kwargs and hasattr(self.device, "set_brightness"):
                        await self.device.set_brightness(int(brightness_pct))
            await self.coordinator.async_request_refresh()
            return

        await super().async_turn_on(**kwargs)


class VeSyncBacklightLightHA(VeSyncBaseEntity, LightEntity):
    """RGB backlight control for VeSync wall switches that support backlight color."""

    _attr_translation_key = "backlight_color"
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_color_mode = ColorMode.RGB

    def __init__(
        self,
        device: VeSyncBaseDevice,
        coordinator: DataUpdateCoordinator,
    ) -> None:
        super().__init__(device, coordinator)
        self._attr_unique_id = f"{self.base_unique_id}-backlight_color"

    @property
    def is_on(self) -> bool:
        return _status_is_on(getattr(getattr(self.device, "state", None), "backlight_status", None))

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        state = getattr(self.device, "state", None)
        if state is None:
            return None

        rgb = getattr(state, "backlight_rgb", None)
        if rgb is not None:
            red = getattr(rgb, "red", None)
            green = getattr(rgb, "green", None)
            blue = getattr(rgb, "blue", None)
            if red is not None and green is not None and blue is not None:
                return (int(red), int(green), int(blue))

        color_obj = getattr(state, "backlight_color", None)
        rgb_obj = getattr(color_obj, "rgb", None) if color_obj is not None else None
        if rgb_obj is not None:
            red = getattr(rgb_obj, "red", None)
            green = getattr(rgb_obj, "green", None)
            blue = getattr(rgb_obj, "blue", None)
            if red is not None and green is not None and blue is not None:
                return (int(red), int(green), int(blue))

        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        rgb = kwargs.get(ATTR_RGB_COLOR)
        if rgb is not None:
            red, green, blue = rgb
            if hasattr(self.device, "set_backlight_color"):
                await self.device.set_backlight_color(int(red), int(green), int(blue))
            elif hasattr(self.device, "set_backlight_status"):
                await self.device.set_backlight_status(True, int(red), int(green), int(blue))
            await self.coordinator.async_request_refresh()
            return

        if hasattr(self.device, "set_backlight_status"):
            await self.device.set_backlight_status(True)
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        if hasattr(self.device, "set_backlight_status"):
            await self.device.set_backlight_status(False)
            await self.coordinator.async_request_refresh()
