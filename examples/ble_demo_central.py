"""
Demonstration of a Bluefruit BLE Central. Connects to the first BLE UART peripheral it finds.
Sends Bluefruit ColorPackets, read from three potentiometers, to the peripheral.
"""

import time

import board
from analogio import AnalogIn

# This hasn't been updated.

#from adafruit_bluefruit_connect.packet import Packet
# Only the packet classes that are imported will be known to Packet.
from adafruit_bluefruit_connect.color_packet import ColorPacket

import adafruit_ble
from adafruit_ble.services.nordic import UARTService
from adafruit_ble.scanner import Scanner

def scale(value):
    """Scale an value from 0-65535 (AnalogIn range) to 0-255 (RGB range)"""
    return int(value / 65535 * 255)

scanner = Scanner()

a3 = AnalogIn(board.A3)
a4 = AnalogIn(board.A4)
a5 = AnalogIn(board.A5)

while True:
    for peer in scanner.scan(UARTService):
        peer.connect()

    r = scale(a3.value)
    g = scale(a4.value)
    b = scale(a5.value)

    color = (r, g, b)
    print(color)
    color_packet = ColorPacket(color)
    for peer in adafruit_ble.peers:
        if not hasattr(peer, "uart"):
            continue
        try:
            peer.uart.write(color_packet.to_bytes())
        except OSError:
            pass
    time.sleep(0.3)
