"""Patches for pyvesync library."""

import logging

_LOGGER = logging.getLogger(__name__)

_PYVESYNC_HUMIDIFIER_LOGGER_NAME = "pyvesync.devices.vesynchumidifier"
_BYPASS_V2_ERROR_SUBSTR = "Error processing bypass V2 API response result"

_PATCHED_GET_DETAILS_ATTR = "__vesync_patched_get_details__"


class _BypassV2HumidifierLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno < logging.ERROR:
            return True

        try:
            message = record.getMessage()
        except Exception:  # noqa: BLE001
            message = str(record.msg)

        return _BYPASS_V2_ERROR_SUBSTR not in message


def apply_patches():
    """Apply patches to pyvesync."""
    try:
        _filter_pyvesync_humidifier_logs()
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Failed to apply pyvesync log filters")

    try:
        _patch_humidifier_get_details()
    except Exception:  # noqa: BLE001
        _LOGGER.exception("Failed to apply pyvesync patches")


def _filter_pyvesync_humidifier_logs() -> None:
    """Filter known-noisy pyvesync humidifier errors.

    Some humidifier models intermittently return a cloud payload that pyvesync
    logs as an error. The integration can recover, so keep logs clean by
    filtering only that specific known message.
    """

    logger = logging.getLogger(_PYVESYNC_HUMIDIFIER_LOGGER_NAME)
    if any(isinstance(f, _BypassV2HumidifierLogFilter) for f in logger.filters):
        return
    logger.addFilter(_BypassV2HumidifierLogFilter())


def _patch_humidifier_get_details() -> None:
    """Patch VeSyncHumidifier.get_details to handle specific errors."""
    try:
        from pyvesync.devices.vesynchumidifier import VeSyncHumidifier
    except Exception:  # noqa: BLE001
        _LOGGER.debug("pyvesync humidifier device class not available; skipping patch")
        return

    if not hasattr(VeSyncHumidifier, "get_details"):
        return

    # Idempotency: `apply_patches()` can be called multiple times (each config entry
    # setup and on reload). Avoid stacking wrappers on wrappers.
    current_get_details = VeSyncHumidifier.get_details
    if getattr(current_get_details, _PATCHED_GET_DETAILS_ATTR, False):
        return

    original_get_details = current_get_details

    def patched_get_details(self, *args, **kwargs):
        try:
            return original_get_details(self, *args, **kwargs)
        except Exception as err:  # noqa: BLE001
            # Suppress specific error for LUH-A602S-WUS and similar
            if _BYPASS_V2_ERROR_SUBSTR in str(err):
                _LOGGER.debug(
                    "Suppressing known error for %s (%s): %s",
                    self.device_name,
                    self.device_type,
                    err,
                )
                return None
            raise

    setattr(patched_get_details, _PATCHED_GET_DETAILS_ATTR, True)
    VeSyncHumidifier.get_details = patched_get_details
