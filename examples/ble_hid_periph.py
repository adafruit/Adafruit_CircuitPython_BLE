"""
Used with ble_demo_central.py. Receives Bluefruit LE ColorPackets from a central,
and updates a NeoPixel FeatherWing to show the history of the received packets.
"""

import adafruit_ble
import board
import sys
import time
from adafruit_ble import SmartAdapter
from adafruit_ble.advertising import to_hex
from adafruit_ble.advertising.standard import ProvideServiceAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

# This has been updated but isn't working.

#pylint: disable=line-too-long
HID_DESCRIPTOR = (
    b'\x05\x01'        # Usage Page (Generic Desktop Ctrls)
    b'\x09\x06'        # Usage (Keyboard)
    b'\xA1\x01'        # Collection (Application)
    b'\x85\x01'        #   Report ID (1)
    b'\x05\x07'        #   Usage Page (Kbrd/Keypad)
    b'\x19\xE0'        #   Usage Minimum (\xE0)
    b'\x29\xE7'        #   Usage Maximum (\xE7)
    b'\x15\x00'        #   Logical Minimum (0)
    b'\x25\x01'        #   Logical Maximum (1)
    b'\x75\x01'        #   Report Size (1)
    b'\x95\x08'        #   Report Count (8)
    b'\x81\x02'        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\x81\x01'        #   Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\x19\x00'        #   Usage Minimum (\x00)
    b'\x29\x65'        #   Usage Maximum (\x65)
    b'\x15\x00'        #   Logical Minimum (0)
    b'\x25\x65'        #   Logical Maximum (101)
    b'\x75\x08'        #   Report Size (8)
    b'\x95\x06'        #   Report Count (6)
    b'\x81\x00'        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\x05\x08'        #   Usage Page (LEDs)
    b'\x19\x01'        #   Usage Minimum (Num Lock)
    b'\x29\x05'        #   Usage Maximum (Kana)
    b'\x15\x00'        #   Logical Minimum (0)
    b'\x25\x01'        #   Logical Maximum (1)
    b'\x75\x01'        #   Report Size (1)
    b'\x95\x05'        #   Report Count (5)
    b'\x91\x02'        #   Output (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    b'\x95\x03'        #   Report Count (3)
    b'\x91\x01'        #   Output (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position,Non-volatile)
    b'\xC0'            # End Collection
    b'\x05\x01'        # Usage Page (Generic Desktop Ctrls)
    b'\x09\x02'        # Usage (Mouse)
    b'\xA1\x01'        # Collection (Application)
    b'\x09\x01'        #   Usage (Pointer)
    b'\xA1\x00'        #   Collection (Physical)
    b'\x85\x02'        #     Report ID (2)
    b'\x05\x09'        #     Usage Page (Button)
    b'\x19\x01'        #     Usage Minimum (\x01)
    b'\x29\x05'        #     Usage Maximum (\x05)
    b'\x15\x00'        #     Logical Minimum (0)
    b'\x25\x01'        #     Logical Maximum (1)
    b'\x95\x05'        #     Report Count (5)
    b'\x75\x01'        #     Report Size (1)
    b'\x81\x02'        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\x95\x01'        #     Report Count (1)
    b'\x75\x03'        #     Report Size (3)
    b'\x81\x01'        #     Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\x05\x01'        #     Usage Page (Generic Desktop Ctrls)
    b'\x09\x30'        #     Usage (X)
    b'\x09\x31'        #     Usage (Y)
    b'\x15\x81'        #     Logical Minimum (-127)
    b'\x25\x7F'        #     Logical Maximum (127)
    b'\x75\x08'        #     Report Size (8)
    b'\x95\x02'        #     Report Count (2)
    b'\x81\x06'        #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
    b'\x09\x38'        #     Usage (Wheel)
    b'\x15\x81'        #     Logical Minimum (-127)
    b'\x25\x7F'        #     Logical Maximum (127)
    b'\x75\x08'        #     Report Size (8)
    b'\x95\x01'        #     Report Count (1)
    b'\x81\x06'        #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
    b'\xC0'            #   End Collection
    b'\xC0'            # End Collection
    b'\x05\x0C'        # Usage Page (Consumer)
    b'\x09\x01'        # Usage (Consumer Control)
    b'\xA1\x01'        # Collection (Application)
    b'\x85\x03'        #   Report ID (3)
    b'\x75\x10'        #   Report Size (16)
    b'\x95\x01'        #   Report Count (1)
    b'\x15\x01'        #   Logical Minimum (1)
    b'\x26\x8C\x02'    #   Logical Maximum (652)
    b'\x19\x01'        #   Usage Minimum (Consumer Control)
    b'\x2A\x8C\x02'    #   Usage Maximum (AC Send)
    b'\x81\x00'        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    b'\xC0'            # End Collection
    # b'\x05\x01'        # Usage Page (Generic Desktop Ctrls)
    # b'\x09\x05'        # Usage (Game Pad)
    # b'\xA1\x01'        # Collection (Application)
    # b'\x85\x05'        #   Report ID (5)
    # b'\x05\x09'        #   Usage Page (Button)
    # b'\x19\x01'        #   Usage Minimum (\x01)
    # b'\x29\x10'        #   Usage Maximum (\x10)
    # b'\x15\x00'        #   Logical Minimum (0)
    # b'\x25\x01'        #   Logical Maximum (1)
    # b'\x75\x01'        #   Report Size (1)
    # b'\x95\x10'        #   Report Count (16)
    # b'\x81\x02'        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    # b'\x05\x01'        #   Usage Page (Generic Desktop Ctrls)
    # b'\x15\x81'        #   Logical Minimum (-127)
    # b'\x25\x7F'        #   Logical Maximum (127)
    # b'\x09\x30'        #   Usage (X)
    # b'\x09\x31'        #   Usage (Y)
    # b'\x09\x32'        #   Usage (Z)
    # b'\x09\x35'        #   Usage (Rz)
    # b'\x75\x08'        #   Report Size (8)
    # b'\x95\x04'        #   Report Count (4)
    # b'\x81\x02'        #   Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    # b'\xC0'            # End Collection
)
#pylint: enable=line-too-long

hid = HIDService(HID_DESCRIPTOR)
device_info = DeviceInfoService(software_revision=adafruit_ble.__version__,
                                manufacturer="Adafruit Industries")
print(device_info.manufacturer)
advertisement = ProvideServiceAdvertisement(hid)
advertisement.appearance = 961

adapter = SmartAdapter()
print(to_hex(bytes(advertisement)))
if not adapter.connected:
    print("advertising")
    adapter.start_advertising(advertisement)
else:
    print("already connected")
    print(adapter.connections)

k = Keyboard(hid.devices)
kl = KeyboardLayoutUS(k)
while True:
    while not adapter.connected:
        pass
    #print("Start typing:")
    while adapter.connected:
        # c = sys.stdin.read(1)
        # sys.stdout.write(c)
        #kl.write(c)
        kl.write("h")
        # print("sleeping")
        time.sleep(0.1)
    adapter.start_advertising(advertisement)
