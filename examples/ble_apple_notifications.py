"""
This example solicits that apple devices that provide notifications connect to it, initiates
pairing, prints existing notifications and then prints any new ones as they arrive.
"""

# TODO: Add support for accessing individual fields.

import adafruit_ble
from adafruit_ble.advertising.standard import SolicitServicesAdvertisement
from adafruit_ble.services.apple import AppleNotificationService
import time

radio = adafruit_ble.BLERadio()
a = SolicitServicesAdvertisement()
a.complete_name = "NotifyPlease"
a.solicited_services.append(AppleNotificationService)
radio.start_advertising(a)

while not radio.connected:
    pass

print("connected")

known_notifications = set()

while radio.connected:
    for connection in radio.connections:
        if not connection.paired:
            connection.pair()
            print("paired")

        ans = connection[AppleNotificationService]
        for notification in ans:
            if notification.id not in known_notifications:
                print(notification)
                known_notifications.add(notification.id)
    time.sleep(1)

print("disconnected")
