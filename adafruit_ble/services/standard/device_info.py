# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
:py:mod:`~adafruit_ble.services.standard.device_info`
=======================================================

"""

from __future__ import annotations

import binascii
import os
import sys

from .. import Service
from ...uuid import StandardUUID
from ...characteristics.string import FixedStringCharacteristic

try:
    from typing import Optional, TYPE_CHECKING

    if TYPE_CHECKING:
        import _bleio

except ImportError:
    pass

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class DeviceInfoService(Service):
    """Device information"""

    uuid = StandardUUID(0x180A)
    model_number = FixedStringCharacteristic(uuid=StandardUUID(0x2A24))
    serial_number = FixedStringCharacteristic(uuid=StandardUUID(0x2A25))
    firmware_revision = FixedStringCharacteristic(uuid=StandardUUID(0x2A26))
    hardware_revision = FixedStringCharacteristic(uuid=StandardUUID(0x2A27))
    software_revision = FixedStringCharacteristic(uuid=StandardUUID(0x2A28))
    manufacturer = FixedStringCharacteristic(uuid=StandardUUID(0x2A29))

    def __init__(
        self,
        *,
        manufacturer: Optional[str] = None,
        software_revision: Optional[str] = None,
        model_number: Optional[str] = None,
        serial_number: Optional[str] = None,
        firmware_revision: Optional[str] = None,
        hardware_revision: Optional[str] = None,
        service: Optional[_bleio.Service] = None,
    ) -> None:
        if not service:
            if model_number is None:
                model_number = sys.platform
            if serial_number is None:
                try:
                    import microcontroller  # pylint: disable=import-outside-toplevel

                    serial_number = binascii.hexlify(
                        microcontroller.cpu.uid  # pylint: disable=no-member
                    ).decode("utf-8")
                except ImportError:
                    pass
            if firmware_revision is None:
                firmware_revision = getattr(os.uname(), "version", None)
        super().__init__(
            manufacturer=manufacturer,
            software_revision=software_revision,
            model_number=model_number,
            serial_number=serial_number,
            firmware_revision=firmware_revision,
            hardware_revision=hardware_revision,
            service=service,
        )
