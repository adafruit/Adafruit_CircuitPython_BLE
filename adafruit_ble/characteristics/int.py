# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`int`
====================================================

This module provides integer characteristics that are usable directly as attributes.

"""

from __future__ import annotations

from . import Attribute, StructCharacteristic

try:
    from typing import TYPE_CHECKING, Optional, Type, Union

    if TYPE_CHECKING:
        from circuitpython_typing import ReadableBuffer

        from adafruit_ble.services import Service
        from adafruit_ble.uuid import UUID

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class IntCharacteristic(StructCharacteristic):
    """Superclass for different kinds of integer fields."""

    def __init__(
        self,
        format_string: str,
        min_value: int,
        max_value: int,
        *,
        uuid: Optional[UUID] = None,
        properties: int = 0,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        initial_value: Optional[ReadableBuffer] = None,
    ) -> None:
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

    def __get__(
        self, obj: Optional[Service], cls: Optional[Type[Service]] = None
    ) -> Union[int, IntCharacteristic]:
        if obj is None:
            return self
        return super().__get__(obj)[0]

    def __set__(self, obj: Service, value: int) -> None:
        if not self._min_value <= value <= self._max_value:
            raise ValueError("out of range")
        super().__set__(obj, (value,))


class Int8Characteristic(IntCharacteristic):
    """Int8 number."""

    def __init__(self, *, min_value: int = -128, max_value: int = 127, **kwargs) -> None:
        super().__init__("<b", min_value, max_value, **kwargs)


class Uint8Characteristic(IntCharacteristic):
    """Uint8 number."""

    def __init__(self, *, min_value: int = 0, max_value: int = 0xFF, **kwargs) -> None:
        super().__init__("<B", min_value, max_value, **kwargs)


class Int16Characteristic(IntCharacteristic):
    """Int16 number."""

    def __init__(self, *, min_value: int = -32768, max_value: int = 32767, **kwargs) -> None:
        super().__init__("<h", min_value, max_value, **kwargs)


class Uint16Characteristic(IntCharacteristic):
    """Uint16 number."""

    def __init__(self, *, min_value: int = 0, max_value: int = 0xFFFF, **kwargs) -> None:
        super().__init__("<H", min_value, max_value, **kwargs)


class Int32Characteristic(IntCharacteristic):
    """Int32 number."""

    def __init__(
        self, *, min_value: int = -2147483648, max_value: int = 2147483647, **kwargs
    ) -> None:
        super().__init__("<i", min_value, max_value, **kwargs)


class Uint32Characteristic(IntCharacteristic):
    """Uint32 number."""

    def __init__(self, *, min_value: int = 0, max_value: int = 0xFFFFFFFF, **kwargs) -> None:
        super().__init__("<I", min_value, max_value, **kwargs)
