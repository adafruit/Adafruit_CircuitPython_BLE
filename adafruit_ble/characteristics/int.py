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

from . import Attribute
from . import StructCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class IntCharacteristic(StructCharacteristic):
    """Superclass for different kinds of integer fields."""

    def __init__(
        self,
        format_string,
        min_value,
        max_value,
        *,
        uuid=None,
        properties=0,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN,
        initial_value=None
    ):
        self._min_value = min_value
        self._max_value = max_value
        if initial_value is not None:
            if not self._min_value <= initial_value <= self._max_value:
                raise ValueError("initial_value out of range")
            initial_value = (initial_value,)

        super().__init__(
            format_string,
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            initial_value=initial_value,
        )

    def __get__(self, obj, cls=None):
        if obj is None:
            return self
        return super().__get__(obj)[0]

    def __set__(self, obj, value):
        if not self._min_value <= value <= self._max_value:
            raise ValueError("out of range")
        super().__set__(obj, (value,))


class Int8Characteristic(IntCharacteristic):
    """Int8 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=-128, max_value=127, **kwargs):
        super().__init__("<b", min_value, max_value, **kwargs)


class Uint8Characteristic(IntCharacteristic):
    """Uint8 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=0, max_value=0xFF, **kwargs):
        super().__init__("<B", min_value, max_value, **kwargs)


class Int16Characteristic(IntCharacteristic):
    """Int16 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=-32768, max_value=32767, **kwargs):
        super().__init__("<h", min_value, max_value, **kwargs)


class Uint16Characteristic(IntCharacteristic):
    """Uint16 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=0, max_value=0xFFFF, **kwargs):
        super().__init__("<H", min_value, max_value, **kwargs)


class Int32Characteristic(IntCharacteristic):
    """Int32 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=-2147483648, max_value=2147483647, **kwargs):
        super().__init__("<i", min_value, max_value, **kwargs)


class Uint32Characteristic(IntCharacteristic):
    """Uint32 number."""

    # pylint: disable=too-few-public-methods
    def __init__(self, *, min_value=0, max_value=0xFFFFFFFF, **kwargs):
        super().__init__("<I", min_value, max_value, **kwargs)
