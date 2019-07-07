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
`adafruit_ble.uart`
====================================================

BLE UART-style communication. Common definitions.

* Author(s): Dan Halbert for Adafruit Industries

"""
from bleio import UUID

NUS_SERVICE_UUID = UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
"""Nordic UART Service UUID"""
NUS_RX_CHAR_UUID = UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")
"""Nordic UART Service RX Characteristic UUID"""
NUS_TX_CHAR_UUID = UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")
"""Nordic UART Service TX Characteristic UUID"""
