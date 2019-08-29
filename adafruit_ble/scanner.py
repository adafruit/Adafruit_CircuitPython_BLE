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

from _bleio import Scanner as _BLEIOScanner
from _bleio import UUID

from .advertising import AdvertisingPacket

class Scanner:
    """
    Scan for BLE device advertisements for a period of time. Return what was received.

    Example::

        from adafruit_ble.scanner import Scanner
        scanner = Scanner()
        scan_entries = scanner.scan(3)  # scan for 3 seconds
    """

    def __init__(self):
        self._scanner = _BLEIOScanner()

    def scan(self, timeout, *, interval=0.1, window=0.1):
        """Scan for advertisements from BLE devices. Suppress duplicates
        in returned `ScanEntry` objects, so there is only one entry per address (device).

        :param int timeout: how long to scan for (in seconds)
        :param float interval: the interval (in seconds) between the start
           of two consecutive scan windows.
           Must be in the range 0.0025 - 40.959375 seconds.
        :param float window: the duration (in seconds) to scan a single BLE channel.
          `window` must be <= `interval`.
        :returns a list of `adafruit_ble.ScanEntry` objects.

        """
        return ScanEntry.unique_devices(self.raw_scan(timeout, interval=interval, window=window))

    def raw_scan(self, timeout, *, interval=0.1, window=0.1):
        """Scan for advertisements from BLE devices. Include every scan entry,
        even duplicates.

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

    :param _bleio.ScanEntry scan_entry: lower-level ScanEntry returned from `_bleio.Scanner`.
      This constructor is normally used only by `Scanner`.
    """

    def __init__(self, scan_entry):
        self._rssi = scan_entry.rssi
        self._address = scan_entry.address
        self._packet = AdvertisingPacket(scan_entry.advertisement_bytes)

    @property
    def advertisement_packet(self):
        """The received advertising packet."""
        return self._packet

    @property
    def rssi(self):
        """The signal strength of the device at the time of the scan. (read-only)."""
        return self._rssi

    @property
    def address(self):
        """The address of the device. (read-only)."""
        return self._address

    @property
    def name(self):
        """The name of the device. (read-only)"""
        name = self._packet.get(AdvertisingPacket.COMPLETE_LOCAL_NAME)
        return name if name else self._packet.get(AdvertisingPacket.SHORT_LOCAL_NAME)

    @property
    def service_uuids(self):
        """List of all the service UUIDs in the advertisement."""
        uuid_values = []

        concat_uuids = self._packet.get(AdvertisingPacket.ALL_16_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self._packet.get(
            AdvertisingPacket.SOME_16_BIT_SERVICE_UUIDS)

        if concat_uuids:
            for i in range(0, len(concat_uuids), 2):
                uuid_values.extend(struct.unpack("<H", concat_uuids[i:i+2]))

        concat_uuids = self._packet.get(AdvertisingPacket.ALL_128_BIT_SERVICE_UUIDS)
        concat_uuids = concat_uuids if concat_uuids else self._packet.get(
            AdvertisingPacket.SOME_128_BIT_SERVICE_UUIDS)

        if concat_uuids:
            for i in range(0, len(concat_uuids), 16):
                uuid_values.append(concat_uuids[i:i+16])

        return [UUID(value) for value in uuid_values]

    @property
    def manufacturer_specific_data(self):
        """Manufacturer-specific data in the advertisement, returned as bytes."""
        return self._packet.get(AdvertisingPacket.MANUFACTURER_SPECIFIC_DATA)

    def same_device(self, other):
        """True if two scan entries appear to be from the same device. Their
        addresses and advertisement must match.
        """
        return (self.address == other.address and
                self.advertisement_packet.packet_bytes ==
                other.advertisement_packet.packet_bytes)

    @staticmethod
    def with_service_uuid(scan_entries, service_uuid):
        """Return all scan entries advertising the given service_uuid."""
        return [se for se in scan_entries if service_uuid in se.service_uuids]

    @staticmethod
    def unique_devices(scan_entries):
        """Discard duplicate scan entries that appear to be from the same device.

        :param sequence scan_entries: ScanEntry objects
        :returns list: list with duplicates removed
        """
        unique = []
        for entry in scan_entries:
            if not any(entry.same_device(unique_entry) for unique_entry in unique):
                unique.append(entry)
        return unique
