# The MIT License (MIT)
#
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries
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
:py:mod:`~adafruit_ble.services.apple`
====================================================

This module provides Services defined by Apple. **Unimplemented.**

"""

from .core import Service
from ..uuid import VendorUUID

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class ContinuityService(Service):
    """Service used for cross-Apple device functionality like AirDrop. Unimplemented."""
    uuid = VendorUUID("d0611e78-bbb4-4591-a5f8-487910ae4366")
    default_field_name = "continuity"

class UnknownApple1Service(Service):
    """Unknown service. Unimplemented."""
    uuid = VendorUUID("9fa480e0-4967-4542-9390-d343dc5d04ae")
    default_field_name = "unknown_apple1"

class AppleNotificationService(Service):
    """Notification service. Unimplemented."""
    uuid = VendorUUID("7905F431-B5CE-4E99-A40F-4B1E122D00D0")
    default_field_name = "apple_notification"

class AppleMediaService(Service):
    """View and control currently playing media. Unimplemented."""
    uuid = VendorUUID("89D3502B-0F36-433A-8EF4-C502AD55F8DC")
    default_field_name = "apple_media"
