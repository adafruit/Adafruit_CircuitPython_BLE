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
`adafruit_ble.hid_keyboard`
====================================================

BLE HID

* Author(s): Dan Halbert for Adafruit Industries

"""
import struct

from micropython import const

# for __version__
import adafruit_ble

from bleio import Attribute, Characteristic, Descriptor, Peripheral, Service, UUID
from .advertising import ServerAdvertisement
from .device_information_service import DeviceInformationService

_HID_SERVICE_UUID_NUM = const(0x1812)
_REPORT_UUID_NUM = const(0x2A4D)
_REPORT_MAP_UUID_NUM = const(0x2A4B)
_HID_INFORMATION_UUID_NUM = const(0x2A4A)
_HID_CONTROL_POINT_UUID_NUM = const(0x2A4C)
_REPORT_REF_DESCR_UUID_NUM = const(0x2908)
_PROTOCOL_MODE_UUID_NUM = const(0x2A4E)

_APPEARANCE_HID_KEYBOARD = const(961)
_APPEARANCE_HID_MOUSE = const(962)
_APPEARANCE_HID_JOYSTICK = const(963)
_APPEARANCE_HID_GAMEPAD = const(964)


# Boot keyboard and mouse not currently supported.
_BOOT_KEYBOARD_INPUT_REPORT_UUID_NUM = const(0x2A22)
_BOOT_KEYBOARD_OUTPUT_REPORT_UUID_NUM = const(0x2A32)
_BOOT_MOUSE_INPUT_REPORT_UUID_NUM = const(0x2A33)

# Output reports not currently implemented (e.g. LEDs on keyboard)
_REPORT_TYPE_INPUT = const(1)
_REPORT_TYPE_OUTPUT = const(2)

# Boot Protocol mode not currently implemented
_PROTOCOL_MODE_BOOT = b'\x00'
_PROTOCOL_MODE_REPORT = b'\x01'

class HIDServer:
    """
    Provide devices for HID over BLE.

    :param str name: Name to advertise for server. If None, use default Peripheral name.

    Example::

        from adafruit_ble.hid_server import HIDServer

        hid = HIDServer()
    """

    # These are used multiple times, so make them class constants.
    _REPORT_UUID = UUID(_REPORT_UUID_NUM)
    _REPORT_REF_DESCR_UUID = UUID(_REPORT_REF_DESCR_UUID_NUM)

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
        # b'\x05\x01'        # Usage Page (Generic Desktop Ctrls)
        # b'\x09\x02'        # Usage (Mouse)
        # b'\xA1\x01'        # Collection (Application)
        # b'\x09\x01'        #   Usage (Pointer)
        # b'\xA1\x00'        #   Collection (Physical)
        # b'\x85\x02'        #     Report ID (2)
        # b'\x05\x09'        #     Usage Page (Button)
        # b'\x19\x01'        #     Usage Minimum (\x01)
        # b'\x29\x05'        #     Usage Maximum (\x05)
        # b'\x15\x00'        #     Logical Minimum (0)
        # b'\x25\x01'        #     Logical Maximum (1)
        # b'\x95\x05'        #     Report Count (5)
        # b'\x75\x01'        #     Report Size (1)
        # b'\x81\x02'        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
        # b'\x95\x01'        #     Report Count (1)
        # b'\x75\x03'        #     Report Size (3)
        # b'\x81\x01'        #     Input (Const,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
        # b'\x05\x01'        #     Usage Page (Generic Desktop Ctrls)
        # b'\x09\x30'        #     Usage (X)
        # b'\x09\x31'        #     Usage (Y)
        # b'\x15\x81'        #     Logical Minimum (-127)
        # b'\x25\x7F'        #     Logical Maximum (127)
        # b'\x75\x08'        #     Report Size (8)
        # b'\x95\x02'        #     Report Count (2)
        # b'\x81\x06'        #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
        # b'\x09\x38'        #     Usage (Wheel)
        # b'\x15\x81'        #     Logical Minimum (-127)
        # b'\x25\x7F'        #     Logical Maximum (127)
        # b'\x75\x08'        #     Report Size (8)
        # b'\x95\x01'        #     Report Count (1)
        # b'\x81\x06'        #     Input (Data,Var,Rel,No Wrap,Linear,Preferred State,No Null Position)
        # b'\xC0'            #   End Collection
        # b'\xC0'            # End Collection
        # b'\x05\x0C'        # Usage Page (Consumer)
        # b'\x09\x01'        # Usage (Consumer Control)
        # b'\xA1\x01'        # Collection (Application)
        # b'\x85\x03'        #   Report ID (3)
        # b'\x75\x10'        #   Report Size (16)
        # b'\x95\x01'        #   Report Count (1)
        # b'\x15\x01'        #   Logical Minimum (1)
        # b'\x26\x8C\x02'    #   Logical Maximum (652)
        # b'\x19\x01'        #   Usage Minimum (Consumer Control)
        # b'\x2A\x8C\x02'    #   Usage Maximum (AC Send)
        # b'\x81\x00'        #   Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
        # b'\xC0'            # End Collection
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

    REPORT_ID_KEYBOARD = 1
    """Keyboard device indicator, for use with `send_report()`."""
    REPORT_ID_MOUSE = 2
    """Mouse device indicator, for use with `send_report()`."""
    REPORT_ID_CONSUMER_CONTROL = 3
    """Consumer control device indicator, for use with `send_report()`."""
    REPORT_ID_GAMEPAD = 5
    """Gamepad device indicator, for use with `send_report()`."""

    _INPUT_REPORT_SIZES = {
        REPORT_ID_KEYBOARD : 8,
        # REPORT_ID_MOUSE : 4,
        # REPORT_ID_CONSUMER_CONTROL : 2,
        # REPORT_ID_GAMEPAD : 6,
    }

    _OUTPUT_REPORT_SIZES = {
        REPORT_ID_KEYBOARD : 1,
    }

    def __init__(self, name=None, tx_power=0):
        self._input_chars = {}
        for report_id in sorted(self._INPUT_REPORT_SIZES.keys()):
            desc = Descriptor(self._REPORT_REF_DESCR_UUID,
                              read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS)
            desc.value = struct.pack('<BB', report_id, _REPORT_TYPE_INPUT)
            report_size = self._INPUT_REPORT_SIZES[report_id]
            self._input_chars[report_id] = Characteristic(
                self._REPORT_UUID, properties=Characteristic.READ | Characteristic.NOTIFY,
                read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS,
                max_length=report_size, fixed_length=True,
                descriptors=(desc,))
            self._input_chars[report_id].value = bytes(report_size)

        self._output_chars = {}
        for report_id in sorted(self._OUTPUT_REPORT_SIZES.keys()):
            desc = Descriptor(self._REPORT_REF_DESCR_UUID,
                              read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS)
            desc.value = struct.pack('<BB', report_id, _REPORT_TYPE_OUTPUT)
            report_size = self._OUTPUT_REPORT_SIZES[report_id]
            self._output_chars[report_id] = Characteristic(
                self._REPORT_UUID,
                properties=(Characteristic.READ | Characteristic.WRITE |
                            Characteristic.WRITE_NO_RESPONSE),
                read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.ENCRYPT_NO_MITM,
                max_length=report_size, fixed_length=True,
                descriptors=(desc,))
            self._output_chars[report_id].value = bytes(report_size)

        # Protocol mode: boot or report. Make it read-only for now because
        # it can't be changed

        # protocol_mode_char = Characteristic(
        #     UUID(_PROTOCOL_MODE_UUID_NUM), properties=Characteristic.READ | Characteristic.WRITE_NO_RESPONSE,
        #     read_perm=Attribute.OPEN, write_perm=Attribute.OPEN,
        #     max_length=1, fixed_length=True)
        # protocol_mode_char.value = _PROTOCOL_MODE_REPORT

        # boot_keyboard_input_report = Characteristic(
        #     UUID(_BOOT_KEYBOARD_INPUT_REPORT_UUID_NUM),
        #     properties=Characteristic.READ | Characteristic.NOTIFY,
        #     read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS,
        #     max_length=self._INPUT_REPORT_SIZES[self.REPORT_ID_KEYBOARD], fixed_length=True)

        # boot_keyboard_output_report = Characteristic(
        #     UUID(_BOOT_KEYBOARD_OUTPUT_REPORT_UUID_NUM),
        #     properties=(Characteristic.READ | Characteristic.WRITE |
        #                 Characteristic.WRITE_NO_RESPONSE),
        #     read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.ENCRYPT_NO_MITM,
        #     max_length=self._OUTPUT_REPORT_SIZES[self.REPORT_ID_KEYBOARD], fixed_length=True)

        # This is the USB HID descriptor (not to be confused with a BLE Descriptor).
        report_map_char = Characteristic(
            UUID(_REPORT_MAP_UUID_NUM), properties=Characteristic.READ,
            read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS,
            max_length=len(self.HID_DESCRIPTOR), fixed_length=True)
        report_map_char.value = self.HID_DESCRIPTOR

        # bcdHID (version), bCountryCode (0 not localized), Flags: RemoteWake, NormallyConnectable
        hid_information_char = Characteristic(
            UUID(_HID_INFORMATION_UUID_NUM), properties=Characteristic.READ,
            read_perm=Attribute.ENCRYPT_NO_MITM, write_perm=Attribute.NO_ACCESS)
        # bcd1.1, country = 0, flag = normal connect
        hid_information_char.value = b'\x01\x01\x00\x02'

        # 0 = suspend; 1 = exit suspend
        self._hid_control_point_char = Characteristic(
            UUID(_HID_CONTROL_POINT_UUID_NUM), properties=Characteristic.WRITE_NO_RESPONSE,
            read_perm=Attribute.NO_ACCESS, write_perm=Attribute.ENCRYPT_NO_MITM)

        # iOS requires Device Information Service. Android does not.
        dis = DeviceInformationService(software_revision=adafruit_ble.__version__,
                                       manufacturer="Adafruit Industries")
        hid_service = Service(UUID(_HID_SERVICE_UUID_NUM),
                              tuple(self._input_chars.values()) +
                              tuple(self._output_chars.values()) +
                              (#boot_keyboard_input_report,
                               #boot_keyboard_output_report,
                               #protocol_mode_char,
                               report_map_char,
                               hid_information_char,
                               self._hid_control_point_char,
                              ))
        self._periph = Peripheral((dis, hid_service), name=name)
        self._advertisement = ServerAdvertisement(self._periph, tx_power=tx_power,
                                                  appearance=_APPEARANCE_HID_KEYBOARD)

    def start_advertising(self):
        """Start advertising the service. When a client connects, advertising will stop.
        When the client disconnects, restart advertising by calling ``start_advertising()`` again.
        """
        self._periph.start_advertising(self._advertisement.advertising_data_bytes,
                                       scan_response=self._advertisement.scan_response_bytes)

    def stop_advertising(self):
        """Stop advertising the service."""
        self._periph.stop_advertising()

    @property
    def connected(self):
        """True if someone connected to the server."""
        return self._periph.connected

    def disconnect(self):
        """Disconnect from peer."""
        self._periph.disconnect()

    def _check_connected(self):
        if not self.connected:
            raise OSError("Not connected")

    def send_report(self, report_id, report):
        """Send a report to the specified device"""
        try:
            self._input_chars[report_id].value = report
        except OSError:
            self._check_connected()
            raise


class HIDDevice:
    """A single HID device: keyboard, mouse, consumer control, or gamepad.

    :param HID hid: The HID object used for BLE communication
    :param int report: The report ID for this device:
      `HID.REPORT_ID_KEYBOARD`, `HID.REPORT_ID_MOUSE`, etc.
    """

    def __init__(self, hid, report_id):
        self._hid = hid
        self._report_id = report_id

    def send_report(self, report):
        """Send a report, via hid"""
        self._hid.send_report(self._report_id, report)
