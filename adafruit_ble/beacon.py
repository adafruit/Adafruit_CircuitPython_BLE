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
`adafruit_ble.beacon`
====================================================

BLE Beacon-related classes.

* Author(s): Dan Halbert for Adafruit Industries

"""

import struct
from _bleio import Peripheral

from .advertising import AdvertisingPacket

class Beacon:
    """Base class for Beacon advertisers."""
    def __init__(self, advertising_packet):
        """Set up a beacon with the given AdvertisingPacket.

        :param AdvertisingPacket advertising_packet
        """
        self._broadcaster = Peripheral()
        self._advertising_packet = advertising_packet

    def start(self, interval=1.0):
        """Turn on beacon.

        :param float interval: Advertising interval in seconds
        """
        self._broadcaster.start_advertising(self._advertising_packet.packet_bytes,
                                            interval=interval)

    def stop(self):
        """Turn off beacon."""
        self._broadcaster.stop_advertising()



class LocationBeacon(Beacon):
    """Advertising Beacon used for position location.
    Used for Apple iBeacon, Nordic nRF Beacon, etc.
    """
    # pylint: disable=too-many-arguments
    def __init__(self, company_id, uuid, major, minor, rssi):
        """Create a beacon with the given values.

        :param int company_id: 16-bit company id designating beacon specification owner
          e.g., 0x004c Apple, 0x0059 Nordic, etc.
        :param UUID uuid: 128-bit UUID unique to application and use case, such as a vendor uuid
        :param int major: 16-bit major number, such as a store number
        :param int minor: 16-bit minor number, such as a location within a store
        :param int rssi: Signal strength in dBm at 1m (signed 8-bit value)

    Example::

        from adafruit_ble.beacon import LocationBeacon
        from adafruit_ble.uuid import UUID
        test_uuid = UUID('12345678-1234-1234-1234-123456789abc')
        test_company = 0xFFFF
        b = LocationBeacon(test_company, test_uuid, 123, 234, -54)
        b.start()
        """

        adv = AdvertisingPacket()
        adv.add_flags()
        adv.add_mfr_specific_data(
            company_id,
            b''.join((
                # 0x02 means a beacon. 0x15 (=21) is length (16 + 2 + 2 + 1)
                # of the rest of the data.
                b'\x02\x15',
                # iBeacon and similar expect big-endian UUIDS. Usually they are little-endian.
                bytes(reversed(uuid.uuid128)),
                # major and minor are big-endian.
                struct.pack(">HHb", major, minor, rssi))))
        super().__init__(adv)


class EddystoneURLBeacon(Beacon):
    """Eddystone-URL protocol beacon.

    Example::

        from adafruit_ble.beacon import EddystoneURLBeacon

        b = EddystoneURLBeacon('https://adafru.it/4062')
        b.start()
    """
    _EDDYSTONE_ID = b'\xAA\xFE'
    # These prefixes are replaced with a single one-byte scheme number.
    _URL_SCHEMES = (
        'http://www.',
        'https://www.',
        'http://',
        'https://'
        )
    # These common domains are replaced with a single non-printing byte.
    # Byte value is 0-6 for these with a '/' suffix.
    # Byte value is 7-13 for these without the '/' suffix.
    _SUBSTITUTIONS = (
        '.com',
        '.org',
        '.edu'
        '.net',
        '.info',
        '.biz',
        '.gov',
    )

    def __init__(self, url, tx_power=0):
        """Create a URL beacon with an encoded version of the url and a transmit power.

        :param url URL to encode. Must be short enough to fit after encoding.
        :param int tx_power: transmit power in dBm at 0 meters (8 bit signed value)
        """

        adv = AdvertisingPacket()
        adv.add_flags()
        adv.add_field(AdvertisingPacket.ALL_16_BIT_SERVICE_UUIDS, self._EDDYSTONE_ID)
        short_url = None
        for idx, prefix in enumerate(self._URL_SCHEMES):
            if url.startswith(prefix):
                short_url = url[len(prefix):]
                url_scheme_num = idx
                break
        if not short_url:
            raise ValueError("url does not start with one of: ", self._URL_SCHEMES)
        for code, subst in enumerate(self._SUBSTITUTIONS):
            short_url = short_url.replace(subst + '/', chr(code))
        for code, subst in enumerate(self._SUBSTITUTIONS, 7):
            short_url = short_url.replace(subst, chr(code))
        adv.add_field(AdvertisingPacket.SERVICE_DATA_16_BIT_UUID,
                      b''.join((self._EDDYSTONE_ID,
                                b'\x10',
                                struct.pack("<bB", tx_power, url_scheme_num),
                                bytes(short_url, 'ascii'))))
        super().__init__(adv)
