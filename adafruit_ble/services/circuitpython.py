# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`circuitpython`
====================================================

This module provides Services defined by CircuitPython. **Out of date.**

"""

from . import Service
from ..characteristics import Characteristic
from ..characteristics.stream import StreamOut
from ..characteristics.string import StringCharacteristic
from ..uuid import VendorUUID

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class CircuitPythonUUID(VendorUUID):
    """UUIDs with the CircuitPython base UUID."""

    def __init__(self, uuid16):
        uuid128 = bytearray("nhtyPtiucriC".encode("utf-8") + b"\x00\x00\xaf\xad")
        uuid128[-3] = uuid16 >> 8
        uuid128[-4] = uuid16 & 0xFF
        super().__init__(uuid128)


class CircuitPythonService(Service):
    """Core CircuitPython service that allows for file modification and REPL access.
    Unimplemented."""

    uuid = CircuitPythonUUID(0x0100)
    filename = StringCharacteristic(
        uuid=CircuitPythonUUID(0x0200),
        properties=(Characteristic.READ | Characteristic.WRITE),
    )
    contents = StreamOut(uuid=CircuitPythonUUID(0x0201))
