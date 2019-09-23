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
`stream`
====================================================

This module provides stream characteristics that bind readable or writable objects to the Service
object they are on.

"""

import _bleio
from .core import ComplexCharacteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class BoundWriteStream:
    """Writes data out to the peer."""
    def __init__(self, stream_out, bound_characteristic):
        self.stream_out = stream_out
        self.bound_characteristic = bound_characteristic

    def write(self, buf):
        """Write data from buf out to the peer."""
        # We can only write 20 bytes at a time.
        offset = 0
        while offset < len(buf):
            self.stream_out.write_raw_data(self.bound_characteristic, buf[offset:offset+20])
            offset += 20

class StreamOut(ComplexCharacteristic):
    """Output stream from the Service server."""
    def __init__(self, *, timeout=1.0, buffer_size=64, **kwargs):
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(properties=_bleio.Characteristic.NOTIFY,
                         read_perm=_bleio.Attribute.OPEN,
                         **kwargs)

    def bind(self, obj, *, initial_value=None):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        # If we're given a characteristic then we're the client and need to buffer in.
        if isinstance(obj, _bleio.Characteristic):
            obj.set_cccd(notify=True)
            return _bleio.CharacteristicBuffer(obj,
                                               timeout=self._timeout,
                                               buffer_size=self._buffer_size)
        bound_characteristic = super().bind(obj, initial_value=initial_value)
        return BoundWriteStream(self, bound_characteristic)

class StreamIn(ComplexCharacteristic):
    """Input stream into the Service server."""
    def __init__(self, *, timeout=1.0, buffer_size=64, **kwargs):
        self._timeout = timeout
        self._buffer_size = buffer_size
        super().__init__(properties=(_bleio.Characteristic.WRITE |
                                     _bleio.Characteristic.WRITE_NO_RESPONSE),
                         read_perm=_bleio.Attribute.NO_ACCESS,
                         write_perm=_bleio.Attribute.OPEN,
                         **kwargs)

    def bind(self, obj, *, initial_value=None):
        """Binds the characteristic to the local Service or remote Characteristic object given."""
        # If we're given a characteristic then we're the client and need to write out.
        if isinstance(obj, _bleio.Characteristic):
            return BoundWriteStream(self, obj)
        # We're the server so buffer incoming writes.
        bound_characteristic = super().bind(obj, initial_value=initial_value)
        return _bleio.CharacteristicBuffer(bound_characteristic,
                                           timeout=self._timeout,
                                           buffer_size=self._buffer_size)
