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
`int`
====================================================

This module provides integer characteristics that are usable directly as attributes.

"""

from .core import StructCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class Uint8Characteristic(StructCharacteristic):
    """Uint8 number."""
    # TODO: Valid set values as within range.
    def __init__(self, *, min_value=0, max_value=255, **kwargs):
        self._min_value = min_value
        self._max_value = max_value
        if "initial_value" in kwargs:
            kwargs["initial_value"] = (kwargs["initial_value"],)
        super().__init__("<B", **kwargs)

    def __get__(self, obj, cls=None):
        return super().__get__(obj)[0]

    def __set__(self, obj, value):
        if not self._min_value <= value <= self._max_value:
            raise ValueError("out of range")
        super().__set__(obj, (value,))
