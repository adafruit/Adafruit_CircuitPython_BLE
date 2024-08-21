# SPDX-FileCopyrightText: 2022 Scott Shawcroft for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Used with ble_packet_buffer_test.py. Transmits "echo" to
PacketBufferService and receives it back.
"""

import time

from ble_packet_buffer_service import PacketBufferService

from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement

ble = BLERadio()
buf = bytearray(512)
while True:
    while ble.connected and any(
        map(
            lambda conn: conn is not None and PacketBufferService in conn,
            ble.connections,
        )
    ):
        for connection in ble.connections:
            if connection is None:
                raise RuntimeError

            if PacketBufferService not in connection:
                continue
            print("echo")

            pb = connection[PacketBufferService]
            if pb is None:
                raise RuntimeError
            pb.write(b"echo")
            # Returns 0 if nothing was read.
            packet_len = pb.readinto(buf)
            if packet_len > 0:
                print(buf[:packet_len])
            print()
        time.sleep(1)

    print("disconnected, scanning")
    for advertisement in ble.start_scan(ProvideServicesAdvertisement, timeout=1):
        if PacketBufferService not in advertisement.services:
            continue
        ble.connect(advertisement)
        print("connected")
        break
    ble.stop_scan()
