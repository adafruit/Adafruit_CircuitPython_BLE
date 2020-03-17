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

This module provides core Unique ID (UUID) classes.

"""

import struct

import _bleio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class UUID:
    """Top level UUID"""

    # TODO: Make subclassing _bleio.UUID work so we can just use it directly.
    # pylint: disable=no-member
    def __hash__(self):
        return hash(self.bleio_uuid)

    def __eq__(self, other):
        if isinstance(other, _bleio.UUID):
            return self.bleio_uuid == other
        if isinstance(other, UUID):
            return self.bleio_uuid == other.bleio_uuid
        return False

    def __str__(self):
        return str(self.bleio_uuid)

    def __bytes__(self):
        if self.bleio_uuid.size == 128:
            return self.bleio_uuid.uuid128
        b = bytearray(2)
        self.bleio_uuid.pack_into(b)
        return bytes(b)

    def pack_into(self, buffer, offset=0):
        """Packs the UUID into the buffer at the given offset."""
        self.bleio_uuid.pack_into(buffer, offset=offset)


class StandardUUID(UUID):
    """Standard 16-bit UUID defined by the Bluetooth SIG."""

    def __init__(self, uuid16):
        if not isinstance(uuid16, int):
            uuid16 = struct.unpack("<H", uuid16)[0]
        self.bleio_uuid = _bleio.UUID(uuid16)
        self.size = 16


class VendorUUID(UUID):
    """Vendor defined, 128-bit UUID."""

    def __init__(self, uuid128):
        self.bleio_uuid = _bleio.UUID(uuid128)
        self.size = 128
