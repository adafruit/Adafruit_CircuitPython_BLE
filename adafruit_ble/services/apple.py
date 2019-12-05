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
import time

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

class _NotificationAttribute:
    def __init__(self, attribute_id, *, max_length=False):
        self._id = attribute_id
        self._max_length = max_length

    def __get__(self, notification, cls):
        if self._id in notification._attribute_cache:
            return notification._attribute_cache[self._id]

        if self._max_length:
            command = struct.pack("<BIBH", 0, notification.id, self._id, 255)
        else:
            command = struct.pack("<BIB", 0, notification.id, self._id)
        notification.control_point.write(command)
        while notification.data_source.in_waiting == 0:
            pass

        _, _ = struct.unpack("<BI", notification.data_source.read(5))
        attribute_id, attribute_length = struct.unpack("<BH", notification.data_source.read(3))
        if attribute_id != self._id:
            raise RuntimeError("Data for other attribute")
        value = notification.data_source.read(attribute_length)
        value = value.decode("utf-8")
        notification._attribute_cache[self._id] = value
        return value

NOTIFICATION_CATEGORIES = (
    "Other",
    "IncomingCall",
    "MissedCall",
    "Voicemail",
    "Social",
    "Schedule",
    "Email",
    "News",
    "HealthAndFitness",
    "BusinessAndFinance",
    "Location",
    "Entertainment"
)

class Notification:
    """One notification that appears in the iOS notification center."""
    # pylint: disable=too-many-instance-attributes

    app_id = _NotificationAttribute(0)
    """String id of the app that generated the notification. It is not the name of the app. For
       example, Slack is "com.tinyspeck.chatlyio" and Twitter is "com.atebits.Tweetie2"."""

    title = _NotificationAttribute(1, max_length=True)
    """Title of the notification. Varies per app."""

    subtitle = _NotificationAttribute(2, max_length=True)
    """Subtitle of the notification. Varies per app."""

    message = _NotificationAttribute(3, max_length=True)
    """Message body of the notification. Varies per app."""

    message_size = _NotificationAttribute(4)
    """Total length of the message string."""

    _raw_date = _NotificationAttribute(5)
    positive_action_label = _NotificationAttribute(6)
    """Human readable label of the positive action."""

    negative_action_label = _NotificationAttribute(7)
    """Human readable label of the negative action."""

    def __init__(self, notification_id, event_flags, category_id, category_count, *, control_point,
                 data_source):
        self.id = notification_id # pylint: disable=invalid-name
        """Integer id of the notification."""

        self.removed = False
        """True when the notification has been cleared on the iOS device."""


        self.silent = False
        self.important = False
        self.preexisting = False
        """True if the notification existed before we connected to the iOS device."""

        self.positive_action = False
        """True if the notification has a positive action to respond with. For example, this could
           be answering a phone call."""

        self.negative_action = False
        """True if the notification has a negative action to respond with. For example, this could
           be declining a phone call."""

        self.category_count = 0
        """Number of other notifications with the same category."""

        self.update(event_flags, category_id, category_count)

        self._attribute_cache = {}

        self.control_point = control_point
        self.data_source = data_source

    def update(self, event_flags, category_id, category_count):
        """Update the notification and clear the attribute cache."""
        self.category_id = category_id

        self.category_count = category_count

        self.silent = (event_flags & (1 << 0)) != 0
        self.important = (event_flags & (1 << 1)) != 0
        self.preexisting = (event_flags & (1 << 2)) != 0
        self.positive_action = (event_flags & (1 << 3)) != 0
        self.negative_action = (event_flags & (1 << 4)) != 0

        self._attribute_cache = {}

    def __str__(self):
        # pylint: disable=too-many-branches
        flags = []
        category = None
        if self.category_id < len(NOTIFICATION_CATEGORIES):
            category = NOTIFICATION_CATEGORIES[self.category_id]

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
        return (category + " " +
                " ".join(flags) + " " +
                self.app_id + " " +
                str(self.title) + " " +
                str(self.subtitle) + " " +
                str(self.message))

class AppleNotificationService(Service):
    """Notification service."""
    uuid = VendorUUID("7905F431-B5CE-4E99-A40F-4B1E122D00D0")

    control_point = StreamIn(uuid=VendorUUID("69D1D8F3-45E1-49A8-9821-9BBDFDAAD9D9"))
    data_source = StreamOut(uuid=VendorUUID("22EAC6E9-24D6-4BB5-BE44-B36ACE7C7BFB"),
                            buffer_size=1024)
    notification_source = StreamOut(uuid=VendorUUID("9FBF120D-6301-42D9-8C58-25E699A21DBD"),
                                    buffer_size=8*100)

    def __init__(self, service=None):
        super().__init__(service=service)
        self._active_notifications = {}

    def _update(self):
        # Pylint is incorrectly inferring the type of self.notification_source so disable no-member.
        while self.notification_source.in_waiting > 7: # pylint: disable=no-member
            buffer = self.notification_source.read(8) # pylint: disable=no-member
            event_id, event_flags, category_id, category_count, nid = struct.unpack("<BBBBI",
                                                                                    buffer)
            if event_id == 0:
                self._active_notifications[nid] = Notification(nid, event_flags, category_id,
                                                               category_count,
                                                               control_point=self.control_point,
                                                               data_source=self.data_source)
                yield self._active_notifications[nid]
            elif event_id == 1:
                self._active_notifications[nid].update(event_flags, category_id, category_count)
                yield None
            elif event_id == 2:
                self._active_notifications[nid].removed = True
                del self._active_notifications[nid]
                yield None

    def wait_for_new_notifications(self, timeout=None):
        """Waits for new notifications and yields them. Returns on timeout, update, disconnect or
           clear."""
        start_time = time.monotonic()
        while timeout is None or timeout > time.monotonic() - start_time:
            try:
                new_notification = next(self._update())
            except StopIteration:
                return
            if new_notification:
                yield new_notification

    @property
    def active_notifications(self):
        """A dictionary of active notifications keyed by id."""
        for _ in self._update():
            pass
        return self._active_notifications

class AppleMediaService(Service):
    """View and control currently playing media. Unimplemented."""
    uuid = VendorUUID("89D3502B-0F36-433A-8EF4-C502AD55F8DC")
