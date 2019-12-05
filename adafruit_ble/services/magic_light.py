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
:py:mod:`~adafruit_ble.services.magic_light`
====================================================

This module provides Services available on a Magic Light, BLE RGB light bulb.

"""

from . import Service
from ..uuid import VendorUUID
from ..characteristics import Characteristic

__version__ = "0.0.0-auto.0"

class MagicLightService(Service):
    # These UUIDs actually use the standard base UUID even though they aren't standard.
    uuid = VendorUUID("0000ffe5-0000-1000-8000-00805f9b34fb")

    _control = Characteristic(uuid=VendorUUID("0000ffe9-0000-1000-8000-00805f9b34fb"), max_length=7)

    def __init__(self, service=None):
        super().__init__(service=service)
        self._color = 0xffffff
        self._buf = bytearray(7)
        self._buf[0] = 0x56
        self._buf[6] = 0xaa
        self._brightness = 1.0

    def __getitem__(self, index):
        if index > 0:
            raise IndexError()
        return self._color

    def __setitem__(self, index, value):
        if index > 0:
            raise IndexError()
        if isinstance(value, int):
            r = (value >> 16) & 0xff
            g = (value >> 8) & 0xff
            b = value & 0xff
        else:
            r, g, b = value
        self._buf[1] = r
        self._buf[2] = g
        self._buf[3] = b
        self._buf[4] = 0x00
        self._buf[5] = 0xf0
        self._control = self._buf
        self._color = value

    def __len__(self):
        return 1

    # Brightness doesn't preserve the color so comment it out for now. There are many other
    # characteristics to try that may.
    # @property
    # def brightness(self):
    #     return self._brightness
    #
    # @brightness.setter
    # def brightness(self, value):
    #     for i in range(3):
    #         self._buf[i + 1] = 0x00
    #     self._buf[4] = int(0xff * value)
    #     self._buf[5] = 0x0f
    #     self._control = self._buf
    #     self._brightness = value
