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
`adafruit`
====================================================

This module provides Adafruit defined advertisements.

Adafruit manufacturing data is key encoded like advertisement data and the Apple manufacturing data.
However, the keys are 16-bits to enable many different uses. Keys above 0xf000 can be used by
Adafruit customers for their own data.

"""

from . import Advertisement, LazyField
from .standard import ManufacturerData, ManufacturerDataField

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class AdafruitColor(Advertisement):
    """Broadcast a single RGB color."""
    prefix = b"\x06\xff\xff\xff\x06\x00\x00"
    manufacturer_data = LazyField(ManufacturerData,
                                  "manufacturer_data",
                                  advertising_data_type=0xff,
                                  company_id=0x0822,
                                  key_encoding="<H")
    color = ManufacturerDataField(0x0000, "<I")

# TODO: Add radio packets.
#
# class AdafruitRadio(Advertisement):
#     prefix = b"\x06\xff\xff\xff\x00\x01"
#
#     channel = Struct()
#     address =
#     group =
#     data =
