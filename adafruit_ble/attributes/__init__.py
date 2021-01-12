# SPDX-FileCopyrightText: 2019 Dan Halbert for Adafruit Industries
#
# SPDX-License-Identifier: MIT

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

       security_mode: authenticated data signing, without man-in-the-middle protection"""

    # pylint: disable=too-few-public-methods
    NO_ACCESS = _bleio.Attribute.NO_ACCESS
    OPEN = _bleio.Attribute.OPEN
    ENCRYPT_NO_MITM = _bleio.Attribute.ENCRYPT_NO_MITM
    ENCRYPT_WITH_MITM = _bleio.Attribute.ENCRYPT_WITH_MITM
    LESC_ENCRYPT_WITH_MITM = _bleio.Attribute.LESC_ENCRYPT_WITH_MITM
    SIGNED_NO_MITM = _bleio.Attribute.SIGNED_NO_MITM
    SIGNED_WITH_MITM = _bleio.Attribute.SIGNED_NO_MITM
