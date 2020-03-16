# The MIT License (MIT)
#
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
