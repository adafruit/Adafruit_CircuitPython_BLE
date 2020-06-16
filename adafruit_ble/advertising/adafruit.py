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

import struct
from micropython import const

from . import Advertisement, LazyObjectField
from .standard import ManufacturerData, ManufacturerDataField

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

_MANUFACTURING_DATA_ADT = const(0xFF)
_ADAFRUIT_COMPANY_ID = const(0x0822)
_COLOR_DATA_ID = const(0x0000)


class AdafruitColor(Advertisement):
    """Broadcast a single RGB color."""

    # This single prefix matches all color advertisements.
    match_prefixes = (
        struct.pack(
            "<BHBH",
            _MANUFACTURING_DATA_ADT,
            _ADAFRUIT_COMPANY_ID,
            struct.calcsize("<HI"),
            _COLOR_DATA_ID,
        ),
    )
    manufacturer_data = LazyObjectField(
        ManufacturerData,
        "manufacturer_data",
        advertising_data_type=_MANUFACTURING_DATA_ADT,
        company_id=_ADAFRUIT_COMPANY_ID,
        key_encoding="<H",
    )
    color = ManufacturerDataField(_COLOR_DATA_ID, "<I")
    """Color to broadcast as RGB integer."""
