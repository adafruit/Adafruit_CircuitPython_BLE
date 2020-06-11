# The MIT License (MIT)
#
# Copyright (c) 2019 Dan Halbert for Adafruit Industries
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
:py:mod:`~adafruit_ble.services.standard.device_info`
=======================================================

"""

import binascii
import os
import sys

from .. import Service
from ...uuid import StandardUUID
from ...characteristics.string import FixedStringCharacteristic

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
        manufacturer=None,
        software_revision=None,
        model_number=None,
        serial_number=None,
        firmware_revision=None,
        hardware_revision=None,
        service=None
    ):
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
