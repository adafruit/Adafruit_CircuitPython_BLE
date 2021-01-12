# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`stream`
====================================================

This module provides stream characteristics that bind readable or writable objects to the Service
object they are on.

"""
import _bleio

from . import Attribute
from . import Characteristic
from . import ComplexCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class BoundWriteStream:
    """Writes data out to the peer."""

    def __init__(self, bound_characteristic):
        self.bound_characteristic = bound_characteristic

    def write(self, buf):
        """Write data from buf out to the peer."""
        # We can only write 20 bytes at a time.
        offset = 0
        while offset < len(buf):
            self.bound_characteristic.value = buf[offset : offset + 20]
            offset += 20


class StreamOut(ComplexCharacteristic):
    """Output stream from the Service server."""

    def __init__(
        self,
        *,
        uuid=None,
        timeout=1.0,
        buffer_size=64,
        properties=Characteristic.NOTIFY,
        read_perm=Attribute.OPEN,
        write_perm=Attribute.OPEN
    ):
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(
            uuid=uuid, properties=properties, read_perm=read_perm, write_perm=write_perm
        )

    def bind(self, service):
        """Binds the characteristic to the given Service."""
        bound_characteristic = super().bind(service)
        # If we're given a remote service then we're the client and need to buffer in.
        if service.remote:
            bound_characteristic.set_cccd(notify=True)
            return _bleio.CharacteristicBuffer(
                bound_characteristic,
                timeout=self._timeout,
                buffer_size=self._buffer_size,
            )
        return BoundWriteStream(bound_characteristic)


class StreamIn(ComplexCharacteristic):
    """Input stream into the Service server."""

    def __init__(
        self,
        *,
        uuid=None,
        timeout=1.0,
        buffer_size=64,
        properties=(Characteristic.WRITE | Characteristic.WRITE_NO_RESPONSE),
        write_perm=Attribute.OPEN
    ):
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(
            uuid=uuid,
            properties=properties,
            read_perm=Attribute.NO_ACCESS,
            write_perm=write_perm,
        )

    def bind(self, service):
        """Binds the characteristic to the given Service."""
        bound_characteristic = super().bind(service)
        # If the service is remote need to write out.
        if service.remote:
            return BoundWriteStream(bound_characteristic)
        # We're the server so buffer incoming writes.
        return _bleio.CharacteristicBuffer(
            bound_characteristic, timeout=self._timeout, buffer_size=self._buffer_size
        )
