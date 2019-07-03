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

Scan for nearby BLE Devices

* Author(s): Dan Halbert for Adafruit Industries

"""
import struct

import bleio

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

    def scan_unique(self, timeout, *, interval=0.1, window=0.1):
        """Scan for advertisements from BLE devices. Suppress duplicates
        in returned `ScanEntry` objects.

        :param int timeout: how long to scan for (in seconds)
        :param float interval: the interval (in seconds) between the start
           of two consecutive scan windows.
           Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
          `window` must be <= `interval`.
        :returns a list of `adafruit_ble.ScanEntry` objects.

        """
        return ScanEntry.unique(self.scan(timeout, interval=interval, window=window))

    def scan(self, timeout, *, interval=0.1, window=0.1):
        """Scan for advertisements from BLE devices.

        :param int timeout: how long to scan for (in seconds)
        :param float interval: the interval (in seconds) between the start
           of two consecutive scan windows.
           Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
          `window` must be <= `interval`.
        :returns a list of `adafruit_ble.ScanEntry` objects.

        """
        return [ScanEntry(e) for e in self._scanner.scan(timeout, interval=interval, window=window)]

class ScanEntry:
    """
    Information about an advertising packet from a BLE device received by a `Scanner`.

    :param bleio.ScanEntry scan_entry: lower-level ScanEntry returned from `bleio.Scanner`.
      This constructor is normally used only by `Scanner`.
    """

    def __init__(self, scan_entry):
        self._bleio_scan_entry = scan_entry

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
                # Type doesn't match: skip to next item.
                i += item_length + 1
            else:
                return adv_bytes[i + 2:i + 1 + item_length]
        return None

    @property
    def advertisement_bytes(self):
        """The raw bytes of the received advertisement."""
        return self._bleio_scan_entry.advertisement_bytes

    @property
    def rssi(self):
        """The signal strength of the device at the time of the scan. (read-only)."""
        return self._bleio_scan_entry.rssi

    @property
    def address(self):
        """The address of the device. (read-only)."""
        return self._bleio_scan_entry.address

    @property
    def name(self):
        """The name of the device. (read-only)"""
        name = self.item(AdvertisingPacket.COMPLETE_LOCAL_NAME)
        return name if name else self.item(AdvertisingPacket.SHORT_LOCAL_NAME)

    @property
    def service_uuids(self):
        """List of all the service UUIDs in the advertisement."""
        uuid_values = []

        concat_uuids = self.item(AdvertisingPacket.ALL_16_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self.item(
            AdvertisingPacket.SOME_16_BIT_SERVICE_UUIDS)

        if concat_uuids:
            for i in range(0, len(concat_uuids), 2):
                uuid_values.append(struct.unpack("<H", concat_uuids[i:i+2]))

        concat_uuids = self.item(AdvertisingPacket.ALL_128_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self.item(
            AdvertisingPacket.SOME_128_BIT_SERVICE_UUIDS)

        if concat_uuids:
            for i in range(0, len(concat_uuids), 16):
                uuid_values.append(concat_uuids[i:i+16])

        print(uuid_values)
        return [bleio.UUID(value) for value in uuid_values]

    @property
    def manufacturer_specific_data(self):
        """Manufacturer-specific data in the advertisement, returned as bytes."""
        return self.item(AdvertisingPacket.MANUFACTURER_SPECIFIC_DATA)

    def matches(self, other):
        """True if two scan entries appear to be from the same device. Their
        addresses and advertisement_bytes must match.
        """
        return (self.address == other.address and
                self.advertisement_bytes == other.advertisement_bytes)

    @staticmethod
    def with_service_uuid(scan_entries, service_uuid):
        """Return all scan entries advertising the given service_uuid."""
        return [se for se in scan_entries if service_uuid in se.service_uuids]

    @staticmethod
    def unique(scan_entries):
        """Discard duplicate scan entries that appear to be from the same device.

        :param sequence scan_entries: ScanEntry objects
        :returns list: list with duplicates removed
        """
        unique = []
        for entry in scan_entries:
            if not any(entry.matches(unique_entry) for unique_entry in unique):
                unique.append(entry)
        return unique
