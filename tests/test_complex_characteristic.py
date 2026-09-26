# SPDX-FileCopyrightText: 2026 Rupayon
#
# SPDX-License-Identifier: MIT

"""Host-side contract tests for ComplexCharacteristic binding."""

import unittest
from unittest.mock import patch

from adafruit_ble.characteristics import ComplexCharacteristic


class ComplexCharacteristicBindingTests(unittest.TestCase):
    def test_fixed_length_option_is_forwarded_to_bleio(self):
        service = type("ServiceStub", (), {"remote": False, "bleio_service": object()})()
        uuid = type("UUIDStub", (), {"bleio_uuid": object()})()

        for fixed_length in (True, False):
            with self.subTest(fixed_length=fixed_length):
                characteristic = ComplexCharacteristic(uuid=uuid, fixed_length=fixed_length)
                with patch(
                    "adafruit_ble.characteristics._bleio.Characteristic.add_to_service"
                ) as add_to_service:
                    characteristic.bind(service)
                self.assertEqual(add_to_service.call_args.kwargs["fixed_length"], fixed_length)


if __name__ == "__main__":
    unittest.main()
