# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`float`
====================================================

This module provides float characteristics that are usable directly as attributes.

"""

from __future__ import annotations

from . import Attribute, StructCharacteristic

try:
    from typing import TYPE_CHECKING, Optional, Type, Union, overload

    if TYPE_CHECKING:
        from circuitpython_typing import ReadableBuffer

        from adafruit_ble.characteristics import Characteristic
        from adafruit_ble.services import Service
        from adafruit_ble.uuid import UUID

except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class FloatCharacteristic(StructCharacteristic):
    """32-bit float"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        *,
        uuid: Optional[UUID] = None,
        properties: int = 0,
        read_perm: int = Attribute.OPEN,
        write_perm: int = Attribute.OPEN,
        initial_value: Optional[ReadableBuffer] = None,
    ) -> None:
        if initial_value is not None:
            initial_value = (initial_value,)
        super().__init__(
            "<f",
            uuid=uuid,
            properties=properties,
            read_perm=read_perm,
            write_perm=write_perm,
            initial_value=initial_value,
        )

    if TYPE_CHECKING:

        @overload
        def __get__(
            self, obj: None, cls: Optional[Type[Service]] = None
        ) -> Characteristic:
            ...

        @overload
        def __get__(self, obj: Service, cls: Optional[Type[Service]] = None) -> float:
            ...

    def __get__(
        self, obj: Optional[Service], cls: Optional[Type[Service]] = None
    ) -> Union[Characteristic, float]:
        if obj is None:
            return self
        get = super().__get__(obj)
        if get is None:
            msg = "Unreachable?"
            raise RuntimeError(msg)
        return get[0]  # pylint: disable=unsubscriptable-object

    def __set__(self, obj: Service, value: float) -> None:
        super().__set__(obj, (value,))
