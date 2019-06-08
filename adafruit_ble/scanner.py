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
`adafruit_ble.scanner`
====================================================

UART-style communication.

* Author(s): Dan Halbert for Adafruit Industries

"""
import struct

import bleio.ScanEntry
import bleio.Scanner
import bleio.UUID

from .advertising import AdvertisingPacket

class Scanner:
    """
    Scan for BLE device advertisements for a period of time. Return what was received.

    Example::

        from adafruit_ble.scanner import Scanner
        scanner = Scanner()
        scanner.Scan

        # Wait for a connection.
        while not uart.connected:
            pass

        uart.write('abc')
    """

    def __init__(self):
        self._scanner = bleio.Scanner()

    def scan(self, timeout, *, interval=0.1, window=0.1):
        """Scan for advertisements from BLE devices.

        :param int timeout: how long to scan for (in seconds)
        :param float interval: the interval (in seconds) between the start
           of two consecutive scan windows.
           Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
          `window` must be <= `interval`.
        :returns: advertising packets found
        :rtype: list of `adafruit_ble.ScanEntry` objects
        """
        return [ScanEntry(entry) for entry in self._scanner.scan(timeout, interval, window)]


class ScanEntry:
    """
    Information about a single transmission of data from a BLE device received by a `Scanner`.

    :param bleio.ScanEntry entry: lower-level ScanEntry from a `bleio.Scanner`.

    This constructor would normally only be used by `Scanner`.
    """

    def __init__(self, entry):
        self._bleio_entry = entry

    def item(self, item_type):
        """Return the bytes in the advertising packet for given the element type.

        :param int element_type: An integer designating an element type.
           A number are defined in `AdvertisingPacket`, such as `AdvertisingPacket.TX_POWER`.
        :returns: bytes that are the value for the given element type.
           If the element type is not present in the packet, return ``None``.
        """
        i = 0
        adv_bytes = self.advertisement_bytes
        while i < len(adv_bytes):
            item_length = adv_bytes[i]
            if  item_type != adv_bytes[i+1]:
                # Type doesn't match: skip to next item
                i += item_length + 1
            else:
                return adv_bytes[i + 2:i + item_length]
        return None

    @property
    def advertisement_bytes(self):
        """The raw bytes of the received advertisement."""
        return self._bleio_entry.raw_data

    @property
    def rssi(self):
        """The signal strength of the device at the time of the scan. (read-only)."""
        return self._bleio_entry.rssi

    @property
    def address(self):
        """The address of the device. (read-only)."""
        return self._bleio_entry.address

    @property
    def name(self):
        """The name of the device. (read-only)"""
        name = self.item(AdvertisingPacket.COMPLETE_LOCAL_NAME)
        return name if name else self.item(AdvertisingPacket.SHORT_LOCAL_NAME)

    @property
    def service_uuids(self):
        """List of all the service UUIDs in the advertisement."""
        concat_uuids = self.item(AdvertisingPacket.ALL_16_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self.item(
            AdvertisingPacket.SOME_16_BIT_SERVICE_UUIDS)

        uuid_values = []
        if concat_uuids:
            for i in range(0, len(uuid_values), 2):
                uuid_values.append(struct.unpack("<H", concat_uuids[i:i+2]))

        concat_uuids = self.item(AdvertisingPacket.ALL_128_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self.item(
            AdvertisingPacket.SOME_128_BIT_SERVICE_UUIDS)

        if concat_uuids:
            for i in range(0, len(uuid_values), 16):
                uuid_values.append(concat_uuids[i:i+16])

        return [bleio.UUID(value) for value in uuid_values]

    @property
    def manufacturer_specific_data(self):
        """Manufacturer-specific data in the advertisement, returned as bytes."""
        return self.item(AdvertisingPacket.MANUFACTURER_SPECIFIC_DATA)