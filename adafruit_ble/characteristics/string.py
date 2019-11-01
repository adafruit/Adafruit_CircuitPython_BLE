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
`string`
====================================================

This module provides string characteristics.

"""

import _bleio
from . import Characteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class StringCharacteristic(Characteristic):
    """UTF-8 Encoded string characteristic."""
    def __init__(self, *, properties=_bleio.Characteristic.READ, uuid=None):
        super().__init__(properties=properties,
                         read_perm=_bleio.Attribute.OPEN,
                         max_length=512,
                         fixed_length=False,
                         uuid=uuid)

    def __get__(self, obj, cls=None):
        raw_data = super().__get__(obj, cls)
        return str(raw_data, "utf-8")

    def __set__(self, obj, value):
        encoded_value = value.encode("utf-8")
        super().__set__(obj, encoded_value)

class FixedStringCharacteristic(Characteristic):
    """Fixed strings are set once when bound and unchanged after."""
    def __init__(self, *, uuid=None):
        super().__init__(properties=_bleio.Characteristic.READ,
                         read_perm=_bleio.Attribute.OPEN,
                         write_perm=_bleio.Attribute.NO_ACCESS,
                         fixed_length=True,
                         uuid=uuid)

    def __get__(self, obj, cls=None):
        raw_data = super().__get__(obj, cls)
        return str(raw_data, "utf-8")
