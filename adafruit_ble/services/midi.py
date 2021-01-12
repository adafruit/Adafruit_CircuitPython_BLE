# SPDX-FileCopyrightText: 2019 Scott Shawcroft for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""
`midi`
====================================================

This module provides Services defined by the MIDI group.

"""

from . import Service
from ..uuid import VendorUUID
from ..characteristics import Characteristic

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class MidiIOCharacteristic(Characteristic):
    """Workhorse MIDI Characteristic that carries midi messages both directions. Unimplemented."""

    # pylint: disable=too-few-public-methods
    uuid = VendorUUID("7772E5DB-3868-4112-A1A9-F2669D106BF3")

    def __init__(self, **kwargs):
        super().__init__(
            properties=(
                Characteristic.NOTIFY
                | Characteristic.READ
                | Characteristic.WRITE
                | Characteristic.WRITE_NO_RESPONSE
            ),
            **kwargs,
        )


class MidiService(Service):
    """BLE Service that transports MIDI messages. Unimplemented."""

    uuid = VendorUUID("03B80E5A-EDE8-4B33-A751-6CE34EC4C700")
    io = MidiIOCharacteristic()  # pylint: disable=invalid-name

    # pylint: disable=unnecessary-pass
    def write(self):
        """Placeholder for transmitting midi bytes to the other device."""
        pass
        # add timestamp to writes 13-bit millisecond resolution
        # prepend one header byte with high timestamp bits 0b10xxxxxx
        # 1. A Running Status MIDI message is allowed within the packet after at least one full MIDI
        #    message.
        # 2. Every MIDI Status byte must be preceded by a timestamp byte. Running Status MIDI may be
        #    preceded by a timestamp byte. If a Running Status MIDI message is not preceded by a
        #    timestamp byte, the timestamp byte of the most recently preceding message in the same
        #    packet is used.
        # 0b1xxxxxxx
        # We need to be able to pack into fixed packet sizes because each packet must start with the
        # high timestamp header byte. Low timestamp packets may wrap around and the decoder is
        # responsible for incrementing the high bits

    def read(self):
        """Placeholder for receiving midi bytes from the other device."""
        pass
