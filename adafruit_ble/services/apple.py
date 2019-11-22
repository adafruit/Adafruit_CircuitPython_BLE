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

import struct

from . import Service
from ..uuid import VendorUUID
from ..characteristics.stream import StreamIn, StreamOut

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_BLE.git"

class ContinuityService(Service):
    """Service used for cross-Apple device functionality like AirDrop. Unimplemented."""
    uuid = VendorUUID("d0611e78-bbb4-4591-a5f8-487910ae4366")

class UnknownApple1Service(Service):
    """Unknown service. Unimplemented."""
    uuid = VendorUUID("9fa480e0-4967-4542-9390-d343dc5d04ae")

class Notification:
    def __init__(self, id, event_flags, category_id, category_count, *, control_point, data_source):
        self.id = id
        self.category_id = category_id
        self.removed = False

        self.silent = (event_flags & (1 << 0)) != 0
        self.important = (event_flags & (1 << 1)) != 0
        self.preexisting = (event_flags & (1 << 2)) != 0
        self.positive_action = (event_flags & (1 << 3)) != 0
        self.negative_action = (event_flags & (1 << 4)) != 0

        self.subtitle = None
        self.message = None

        self.control_point = control_point
        self.data_source = data_source

    def update(self, event_flags, category_id, category_count):
        pass

    def _fetch_all(self):
        self.control_point.write(struct.pack("<BIBBHBHBHBBBB", 0, self.id, 0, 1, 32, 2, 32, 3, 255, 4, 5, 6, 7))
        while self.data_source.in_waiting == 0:
            pass
        _, _ = struct.unpack("<BI", self.data_source.read(5))

        for attribute in ["app_id", "title", "subtitle", "message", "message_size", "date", "positive_action_label", "negative_action_label"]:
            attribute_id, attribute_length = struct.unpack("<BH", self.data_source.read(3))
            if attribute_length == 0:
                continue
            value = self.data_source.read(attribute_length).decode("utf-8")
            setattr(self, attribute, value)

    @property
    def app(self):
        self.control_point.write(struct.pack("<BIB", 0, self.id, 0))
        while self.data_source.in_waiting == 0:
            pass
        print(self.data_source.in_waiting)
        print(self.data_source.read())
        return ""


    def __str__(self):
        self._fetch_all()
        flags = []
        category = None
        if self.category_id == 0:
            category = "Other"
        elif self.category_id == 1:
            category = "IncomingCall"
        elif self.category_id == 2:
            category = "MissedCall"
        elif self.category_id == 3:
            category = "Voicemail"
        elif self.category_id == 4:
            category = "Social"
        elif self.category_id == 5:
            category = "Schedule"
        elif self.category_id == 6:
            category = "Email"
        elif self.category_id == 7:
            category = "News"
        elif self.category_id == 8:
            category = "HealthAndFitness"
        elif self.category_id == 9:
            category = "BusinessAndFinance"
        elif self.category_id == 10:
            category = "Location"
        elif self.category_id == 11:
            category = "Entertainment"

        if self.silent:
            flags.append("silent")
        if self.important:
            flags.append("important")
        if self.preexisting:
            flags.append("preexisting")
        if self.positive_action:
            flags.append("positive_action")
        if self.negative_action:
            flags.append("negative_action")
        return category + " " + " ".join(flags) + " " + self.app_id + " " + self.title + " " + str(self.subtitle) + " " + str(self.message) + " " + self.date

class AppleNotificationService(Service):
    """Notification service."""
    uuid = VendorUUID("7905F431-B5CE-4E99-A40F-4B1E122D00D0")

    control_point = StreamIn(uuid=VendorUUID("69D1D8F3-45E1-49A8-9821-9BBDFDAAD9D9"))
    data_source = StreamOut(uuid=VendorUUID("22EAC6E9-24D6-4BB5-BE44-B36ACE7C7BFB"), buffer_size=1024)
    notification_source = StreamOut(uuid=VendorUUID("9FBF120D-6301-42D9-8C58-25E699A21DBD"), buffer_size=8*100)

    def __init__(self, service=None):
        super().__init__(service=service)
        self._active_notifications = {}

    def _update_notifications(self):
        while self.notification_source.in_waiting > 7:
            buffer = self.notification_source.read(8)
            event_id, event_flags, category_id, category_count, id = struct.unpack("<BBBBI", buffer)
            if event_id == 0:
                self._active_notifications[id] = Notification(id, event_flags, category_id,
                    category_count, control_point=self.control_point, data_source=self.data_source)
            elif event_id == 1:
                self._active_notifications[id].update(event_flags, category_id, category_count)
            elif event_id == 2:
                self._active_notifications[id].removed = True
                del self._active_notifications[id]
            #print(event_id, event_flags, category_id, category_count)

    def __iter__(self):
        self._update_notifications()
        return iter(self._active_notifications.values())

class AppleMediaService(Service):
    """View and control currently playing media. Unimplemented."""
    uuid = VendorUUID("89D3502B-0F36-433A-8EF4-C502AD55F8DC")
