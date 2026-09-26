# SPDX-FileCopyrightText: 2026 Rupayon
#
# SPDX-License-Identifier: MIT

"""Host-side contract tests for UARTService's CharacteristicBuffer calls."""

import unittest

from adafruit_ble.services.nordic import UARTService


class RecordingBuffer:
    def __init__(self):
        self.calls = []

    def readinto(self, buffer, *args):
        self.calls.append((buffer, args))
        if isinstance(buffer, memoryview) and args == (None,):
            raise ValueError("length argument not allowed for this type")
        return min(len(buffer), args[0]) if args else len(buffer)


class UARTReadintoTests(unittest.TestCase):
    def setUp(self):
        self.uart = UARTService.__new__(UARTService)
        self.uart._rx = RecordingBuffer()

    def test_omitted_length_does_not_pass_none_to_characteristic_buffer(self):
        buffer = memoryview(bytearray(4))[1:]
        self.assertEqual(self.uart.readinto(buffer), 3)
        self.assertEqual(self.uart._rx.calls, [(buffer, ())])

    def test_explicit_length_is_forwarded(self):
        buffer = bytearray(4)
        self.assertEqual(self.uart.readinto(buffer, 2), 2)
        self.assertEqual(self.uart._rx.calls, [(buffer, (2,))])


if __name__ == "__main__":
    unittest.main()
