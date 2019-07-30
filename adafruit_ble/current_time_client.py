 # The MIT License (MIT)
#
# Copyright (c) 2019 Dan Halbert for Adafruit Industries
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
`adafruit_ble.current_time_client`
====================================================

UART-style communication by a Central as a GATT Client

* Author(s): Dan Halbert for Adafruit Industries

"""
import struct
import time

from bleio import Peripheral, UUID
from .advertising import SolicitationAdvertisement

class CurrentTimeClient:
    """
    Set up a peripheral that advertises for Current Time Service,
    and connects if found.

    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.current_time_client import CurrentTimeClient

        cts_client = CurrentTimeClient()
        cts_client.start_advertising()
        while not cts_client.connected:
            pass
        cts_client.discover()
        cts_client.pair()
        print(cts_client.current_local_time)
    """

    CTS_UUID = UUID(0x1805)
    CURRENT_TIME_UUID = UUID(0x2A2B)
    LOCAL_TIME_INFORMATION_UUID = UUID(0x2A0F)

    def __init__(self, name="CTSClient", tx_power=0):
        self._periph = Peripheral()
        self._advertisement = SolicitationAdvertisement(name, (self.CTS_UUID,), tx_power=tx_power)
        self._current_time_char = self._local_time_char = None


    def start_advertising(self):
        """Start advertising to solicit a central that supports Current Time Service."""
        self._periph.start_advertising(self._advertisement.advertising_data_bytes,
                                       scan_response=self._advertisement.scan_response_bytes)

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if a central connected to this peripheral."""
        return self._periph.connected

    def disconnect(self):
        """Disconnect from central."""
        self._periph.disconnect()

    def _check_connected(self):
        if not self.connected:
            raise OSError("Not connected")

    def pair(self):
        """Pair with the connected central."""
        self._check_connected()
        self._periph.pair()

    def discover(self):
        """Discover service information."""
        self._check_connected()
        self._periph.discover_remote_services((self.CTS_UUID,))
        services = self._periph.remote_services
        if not services:
            raise OSError("Unable to discover service")
        for characteristic in services[0].characteristics:
            if characteristic.uuid == self.CURRENT_TIME_UUID:
                self._current_time_char = characteristic
            elif characteristic.uuid == self.LOCAL_TIME_INFORMATION_UUID:
                self._local_time_char = characteristic
        if not self._current_time_char or not self._local_time_char:
            raise OSError("Remote service missing needed characteristic")

    @property
    def current_time(self):
        """Get a tuple describing the current time from the server:
        (year, month, day, hour, minute, second, weekday, subsecond, adjust_reason)
        """
        self._check_connected()
        if self._current_time_char:
            # year, month, day, hour, minute, second, weekday, subsecond, adjust_reason
            values = struct.unpack('<HBBBBBBBB', self._current_time_char.value)
            return values
        else:
            raise OSError("Characteristic not discovered")


    @property
    def local_time_information(self):
        """Get a tuple of location information from the server:
        (timezone, dst_offset)
        """
        self._check_connected()
        if self._local_time_char:
            # timezone, dst_offset
            values = struct.unpack('<bB', self._local_time_char.value)
            return values
        else:
            raise OSError("Characteristic not discovered")

    @property
    def struct_time(self):
        """Return the current time as a `time.struct_time` Day of year and whether DST is in effect
        is not available from Current Time Service, so these are set to -1.
        """
        _, month, day, hour, minute, second, weekday, _, _ = self.current_time
        # Bluetooth weekdays count from 1. struct_time counts from 0.
        return time.struct_time((month, day, hour, minute, second, weekday - 1, -1))
