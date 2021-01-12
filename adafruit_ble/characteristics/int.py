# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

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
