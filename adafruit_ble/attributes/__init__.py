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
:py:mod:`~adafruit_ble.attributes`
====================================================

This module provides definitions common to all kinds of BLE attributes,
specifically characteristics and descriptors.

"""
import _bleio

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"


class Attribute:
    """Constants describing security levels.

      .. data:: NO_ACCESS

         security mode: access not allowed

      .. data:: OPEN

         security_mode: no security (link is not encrypted)

      .. data:: ENCRYPT_NO_MITM

         security_mode: unauthenticated encryption, without man-in-the-middle protection

      .. data:: ENCRYPT_WITH_MITM

         security_mode: authenticated encryption, with man-in-the-middle protection

      .. data:: LESC_ENCRYPT_WITH_MITM

         security_mode: LESC encryption, with man-in-the-middle protection

      .. data:: SIGNED_NO_MITM

         security_mode: unauthenticated data signing, without man-in-the-middle protection

      .. data:: SIGNED_WITH_MITM

         security_mode: authenticated data signing, without man-in-the-middle protection
"""

    # pylint: disable=too-few-public-methods
    NO_ACCESS = _bleio.Attribute.NO_ACCESS
    OPEN = _bleio.Attribute.OPEN
    ENCRYPT_NO_MITM = _bleio.Attribute.ENCRYPT_NO_MITM
    ENCRYPT_WITH_MITM = _bleio.Attribute.ENCRYPT_WITH_MITM
    LESC_ENCRYPT_WITH_MITM = _bleio.Attribute.LESC_ENCRYPT_WITH_MITM
    SIGNED_NO_MITM = _bleio.Attribute.SIGNED_NO_MITM
    SIGNED_WITH_MITM = _bleio.Attribute.SIGNED_NO_MITM
