# The MIT License (MIT)
#
# Copyright (c) 2018 Dan Halbert for Adafruit Industries
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
`adafruit_ble.uuid`
====================================================

UUID-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""
import binascii
import struct

import bleio

class UUID:
    """BLE UUIDs, both 16-bit and 128-bit."""
    def __init__(self, value):
        """Create a new immutable object encapsulating the uuid value.

        :param int/buffer value: The uuid value to encapsulate. One of:
            - an `int` value in range 0 to 0xFFFF (Bluetooth SIG 16-bit UUID)
            - a `str` value in the format 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
              where the ``x``'s are hex digits. (128 bit UUID)
            - a buffer object (bytearray, bytes)  of 16 bytes in little-endian order (128-bit UUID)
              Note that the order is reversed from the order of a string-based 128-bit UUID.
            - a `bleio.UUID` object, which simply gets wrapped in this object
        """
        if isinstance(value, bleio.UUID):
            self._bleio_uuid = value
            return
        # Convert string form to bytes if needed.
        if isinstance(value, str):
            if len(value) != 36 or value[8] != '-' or value[13] != '-' or value[23] != '-':
                raise ValueError("UUID string not 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'")
            value = bytes(reversed(binascii.unhexlify(value.replace('-', ''))))
        self._bleio_uuid = bleio.UUID(value)

    @classmethod
    def from_base_uuid(cls, uuid16, base_uuid):
        """Create a new UUID from an existing 128-bit UUID by replacing the 16-bit part.

        :param int uuid16: The value that will replace bytes 12 and 13 of `base_uuid`
        :param UUID base_uuid: The 128-bit UUID to use as a base
        """
        uuid128_bytes = base_uuid.uuid128
        uuid128_bytes[12:14] = struct.pack('<H', uuid16)
        return UUID(uuid128_bytes)

    @property
    def uuid16(self):
        """The 16-bit part of the UUID. May be the whole UUID if it's a 16-bit UUID. (read only)"""
        return self._bleio_uuid.uuid16

    @property
    def uuid128(self):
        """The 128-bit value of the UUID, returned as bytes.
        Raises AttributeError if this is a 16-bit-UUID. (read-only)
        """
        return self._bleio_uuid.uuid128

    @property
    def size(self):
        """The size of the UUID: 16 or 128 bits."""
        return self._bleio_uuid.size

    @property
    def bleio_uuid(self):
        """The native bleio UUID object."""
        return self._bleio_uuid


    def __repr__(self):
        if self.size == 16:
            return 'UUID({:#06x})'.format(self.uuid16)
        return ((
            "UUID('{:02x}{:02x}{:02x}{:02x}-"
            "{:02x}{:02x}-"
            "{:02x}{:02x}-"
            "{:02x}{:02x}-"
            "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}')")
                .format(*reversed(self.uuid128)))
