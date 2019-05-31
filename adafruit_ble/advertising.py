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
`adafruit_ble.advertising`
====================================================

Advertising-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""

import struct

class Advertisement:
    """Build up a BLE advertising data packet."""
    # BR/EDR flags not included here, since we don't support BR/EDR.
    FLAG_LIMITED_DISCOVERY = 0x01
    """Discoverable only for a limited time period."""
    FLAG_GENERAL_DISCOVERY = 0x02
    """Will advertise until discovered."""
    FLAG_LE_ONLY = 0x04
    """BR/EDR not supported."""

    FLAGS = 0x01
    """Discoverability flags."""
    SOME_16_BIT_SERVICE_UUIDS = 0x02
    """Incomplete list of 16 bit service UUIDs."""
    ALL_16_BIT_SERVICE_UUIDS = 0x03
    """Complete list of 16 bit service UUIDs."""
    SOME_128_BIT_SERVICE_UUIDS = 0x06
    """Incomplete list of 128 bit service UUIDs."""
    ALL_128_BIT_SERVICE_UUIDS = 0x07
    """Complete list of 128 bit service UUIDs."""
    SHORT_LOCAL_NAME = 0x08
    """Short local device name (shortened to fit)."""
    COMPLETE_LOCAL_NAME = 0x09
    """Complete local device name."""
    TX_POWER = 0x0A
    """Transmit power level"""
    DEVICE_ID = 0x10
    """Device identifier."""
    SLAVE_CONN_INTERVAL_RANGE = 0x12
    """Slave connection interval range."""
    SERVICE_DATA_16_BIT_UUID = 0x16
    """Service data with 16 bit UUID."""
    PUBLIC_TARGET_ADDRESS = 0x17
    """Public target address."""
    RANDOM_TARGET_ADDRESS = 0x18
    """Random target address (chosen randomly)."""
    APPEARANCE = 0x19
    """Appearance."""
    DEVICE_ADDRESS = 0x1B
    """LE Bluetooth device address."""
    ROLE = 0x1C
    """LE Role."""
    SERVICE_DATA_128BIT_UUID = 0x21
    """Service data with 128 bit UUID."""
    MANUFACTURER_SPECIFIC_DATA = 0xFF
    """Manufacturer-specific data."""

    MAX_DATA_SIZE = 31
    """Data size in a regular BLE packet."""

    def __init__(self, flags=(FLAG_GENERAL_DISCOVERY | FLAG_LE_ONLY), max_length=MAX_DATA_SIZE):
        """Initalize an advertising packet, with the given flags, no larger than max_length."""
        self.data = bytearray((2, self.FLAGS, flags))
        self._max_length = max_length
        self._check_length()

    @property
    def bytes_remaining(self):
        return self._max_length - len(self.data)

    def _check_length(self):
        if len(self.data) > self._max_length:
            raise IndexError("Advertising data too long")

    def add_field(self, field_type, field_data):
        """Append an advertising data field to the current packet, of the given type.
        The length field is calculated from the length of field_data."""
        self.data.append(1 + len(field_data))
        self.data.append(field_type)
        self.data.extend(field_data)
        self._check_length()

    def add_16_bit_uuids(self, uuids):
        """Add a complete list of 16 bit service UUIDs."""
        for uuid in uuids:
            self.add_field(self.ALL_16_BIT_SERVICE_UUIDS, struct.pack("<H", uuid.uuid16))

    def add_128_bit_uuids(self, uuids):
        """Add a complete list of 128 bit service UUIDs."""
        for uuid in uuids:
            self.add_field(self.ALL_128_BIT_SERVICE_UUIDS, uuid.uuid128)

    def add_mfr_specific_data(self, mfr_id, data):
        """Add manufacturer-specific data bytes."""
        self.add_field(self.MANUFACTURER_SPECIFIC_DATA, struct.pack('<H', mfr_id) + data)


class ServerAdvertisement:
    def __init__(self, peripheral, *, tx_power=0):
        """Create an advertisement to advertise a peripheral's services.

        :param peripheral Peripheral the Peripheral to advertise. Use its services and name
        :param int tx_power: transmit power in dBm at 0 meters (8 bit signed value). Default 0 dBm
        """

        self._peripheral = peripheral

        adv = Advertisement()

        # Need to check service.secondary
        uuids_16_bits = [service.uuid for service in peripheral.services
                         if service.uuid.size == 16 and not service.secondary]
        if uuids_16_bits:
            adv.add_16_bit_uuids(uuids_16_bits)

        uuids_128_bits = [service.uuid for service in peripheral.services
                         if service.uuid.size == 128 and not service.secondary]
        if uuids_128_bits:
            adv.add_128_bit_uuids(uuids_128_bits)

        adv.add_field(Advertisement.TX_POWER, struct.pack("<b", tx_power))

        # 2 bytes needed for field length and type.
        bytes_available = adv.bytes_remaining - 2
        if bytes_available <= 0:
            raise IndexError("No room for name")

        name_bytes = bytes(peripheral.name, 'utf-8')
        if bytes_available >= len(name_bytes):
            adv.add_field(Advertisement.COMPLETE_LOCAL_NAME, name_bytes)
        else:
            adv.add_field(Advertisement.SHORT_LOCAL_NAME, name_bytes[:bytes_available])

        self._advertisement = adv

    @property
    def data(self):
        return self._advertisement.data
