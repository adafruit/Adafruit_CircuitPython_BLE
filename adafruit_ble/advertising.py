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

class AdvertisingPacket:
    """Build up a BLE advertising data or scan response packet."""
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
    SOLICITED_16_BIT_SERVICE_UUIDS = 0x14
    """List of 16 bit service UUIDs solicited by a peripheral."""
    SOLICITED_128_BIT_SERVICE_UUIDS = 0x15
    """List of 128 bit service UUIDs solicited by a peripheral."""
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

    def __init__(self, data=None, *, max_length=MAX_DATA_SIZE):
        """Create an advertising packet, no larger than max_length.

        :param buf data: if not supplied (None), create an empty packet
          if supplied, create a packet with supplied data. This is usually used
          to parse an existing packet.
        :param int max_length: maximum length of packet
        """
        self._packet_bytes = bytearray(data) if data else bytearray()
        self._max_length = max_length
        self._check_length()

    @property
    def packet_bytes(self):
        """The raw packet bytes."""
        return self._packet_bytes

    @packet_bytes.setter
    def packet_bytes(self, value):
        self._packet_bytes = value

    def __getitem__(self, element_type):
        """Return the bytes stored in the advertising packet for the given element type.

        :param int element_type: An integer designating an advertising element type.
           A number of types are defined in `AdvertisingPacket`,
           such as `AdvertisingPacket.TX_POWER`.
        :returns: bytes that are the value for the given element type.
           If the element type is not present in the packet, raise KeyError.
        """
        i = 0
        adv_bytes = self.packet_bytes
        while i < len(adv_bytes):
            item_length = adv_bytes[i]
            if  element_type != adv_bytes[i+1]:
                # Type doesn't match: skip to next item.
                i += item_length + 1
            else:
                return adv_bytes[i + 2:i + 1 + item_length]
        raise KeyError

    def get(self, element_type, default=None):
        """Return the bytes stored in the advertising packet for the given element type,
        returning the default value if not found.
        """
        try:
            return self.__getitem__(element_type)
        except KeyError:
            return default

    @property
    def length(self):
        """Current number of bytes in packet."""
        return len(self._packet_bytes)

    @property
    def bytes_remaining(self):
        """Number of bytes still available for use in the packet."""
        return self._max_length - self.length

    def _check_length(self):
        if self.length > self._max_length:
            raise IndexError("Advertising data too long")

    def add_flags(self, flags=(FLAG_GENERAL_DISCOVERY | FLAG_LE_ONLY)):
        """Add advertising flags."""
        self.add_field(self.FLAGS, struct.pack("<B", flags))

    def add_field(self, field_type, field_data):
        """Append byte data to the current packet, of the given type.
        The length field is calculated from the length of field_data."""
        self._packet_bytes.append(1 + len(field_data))
        self._packet_bytes.append(field_type)
        self._packet_bytes.extend(field_data)
        self._check_length()

    def add_mfr_specific_data(self, mfr_id, data):
        """Add manufacturer-specific data bytes."""
        self.add_field(self.MANUFACTURER_SPECIFIC_DATA, struct.pack('<H', mfr_id) + data)

    def add_tx_power(self, tx_power):
        """Add transmit power value."""
        self.add_field(AdvertisingPacket.TX_POWER, struct.pack("<b", tx_power))

    def add_appearance(self, appearance):
        """Add BLE Appearance value."""
        self.add_field(AdvertisingPacket.APPEARANCE, struct.pack("<h", appearance))


class Advertisement:
    """Superclass for common code to construct a BLE advertisement,
    consisting of an advertising data packet and an optional scan response packet.

    :param int flags: advertising flags. Default is general discovery, and BLE only (not classic)
    """
    def __init__(self, flags=None, tx_power=None):
        self._packet = AdvertisingPacket()
        self._scan_response_packet = None
        if flags:
            self._packet.add_flags(flags)
        else:
            self._packet.add_flags()

        if tx_power is not None:
            self._packet.add_tx_power(tx_power)

    def add_name(self, name):
        """Add name to advertisement. If it doesn't fit, add truncated name to packet,
        and add complete name to scan response packet.
        """
        # 2 bytes needed for field length and type.
        bytes_available = self._packet.bytes_remaining - 2
        if bytes_available <= 0:
            raise IndexError("No room for name")

        name_bytes = bytes(name, 'utf-8')
        if bytes_available >= len(name_bytes):
            self._packet.add_field(AdvertisingPacket.COMPLETE_LOCAL_NAME, name_bytes)
        else:
            self._packet.add_field(AdvertisingPacket.SHORT_LOCAL_NAME, name_bytes[:bytes_available])
            self._scan_response_packet = AdvertisingPacket()
            try:
                self._scan_response_packet.add_field(AdvertisingPacket.COMPLETE_LOCAL_NAME,
                                                     name_bytes)
            except IndexError:
                raise IndexError("Name too long")

    def add_uuids(self, uuids, field_type_16_bit_uuids, field_type_128_bit_uuids):
        """Add 16-bit and 128-bit uuids to the packet, using the given field types."""
        concatenated_16_bit_uuids = b''.join(
            struct.pack("<H", uuid.uuid16) for uuid in uuids if uuid.size == 16)
        if concatenated_16_bit_uuids:
            self._packet.add_field(field_type_16_bit_uuids, concatenated_16_bit_uuids)

        uuids_128_bits = [uuid for uuid in uuids if uuid.size == 128]
        if len(uuids_128_bits) > 1:
            raise ValueError("Only one 128 bit UUID will fit")
        if uuids_128_bits:
            self._packet.add_field(field_type_128_bit_uuids, uuids_128_bits[0].uuid128)

    @property
    def advertising_data_bytes(self):
        """The raw bytes for the initial advertising data packet."""
        return self._packet.packet_bytes

    @property
    def scan_response_bytes(self):
        """The raw bytes for the scan response packet. None if there is no response packet."""
        if self._scan_response_packet:
            return self._scan_response_packet.packet_bytes
        return None


class ServerAdvertisement(Advertisement):
    """Build an advertisement for a peripheral's services.

    There is room in the packet for only one 128-bit UUID. Giving UUIDs in the scan response
    is not yet implemented.

    :param Peripheral peripheral: the Peripheral to advertise. Use its services and name.
    :param int tx_power: transmit power in dBm at 0 meters (8 bit signed value). Default 0 dBm
    """

    def __init__(self, peripheral, *, tx_power=0):
        super().__init__()
        uuids = [service.uuid for service in peripheral.services if not service.secondary]
        self.add_uuids(uuids,
                       AdvertisingPacket.ALL_16_BIT_SERVICE_UUIDS,
                       AdvertisingPacket.ALL_128_BIT_SERVICE_UUIDS)
        self.add_name(peripheral.name)


class SolicitationAdvertisement(Advertisement):
    """Build an advertisement for a peripheral to solicit one or more services from a central.

    There is room in the packet for only one 128-bit UUID. Giving UUIDs in the scan response
    is not yet implemented.

    :param string name: Name to use in advertisement.
    :param iterable service_uuids: One or more services requested from a central
    :param int tx_power: transmit power in dBm at 0 meters (8 bit signed value). Default 0 dBm.
    """

    def __init__(self, name, service_uuids, *, tx_power=0):
        super().__init__()
        self.add_uuids(service_uuids,
                       AdvertisingPacket.SOLICITED_16_BIT_SERVICE_UUIDS,
                       AdvertisingPacket.SOLICITED_128_BIT_SERVICE_UUIDS)
        self.add_name(name)
