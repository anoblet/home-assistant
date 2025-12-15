"""Patches for pyvesync library."""
import logging
from pyvesync.devices.vesynchumidifier import VeSyncHumidifier

_LOGGER = logging.getLogger(__name__)

def apply_patches():
    """Apply patches to pyvesync."""
    _patch_humidifier_get_details()

def _patch_humidifier_get_details():
    """Patch VeSyncHumidifier.get_details to handle specific errors."""
    if not hasattr(VeSyncHumidifier, "get_details"):
        return

    original_get_details = VeSyncHumidifier.get_details

    def patched_get_details(self):
        try:
            original_get_details(self)
        except Exception as err:
            # Suppress specific error for LUH-A602S-WUS and similar
            if "Error processing bypass V2 API response result" in str(err):
                _LOGGER.debug(
                    "Suppressing known error for %s (%s): %s",
                    self.device_name,
                    self.device_type,
                    err,
                )
            else:
                raise err

    VeSyncHumidifier.get_details = patched_get_details
