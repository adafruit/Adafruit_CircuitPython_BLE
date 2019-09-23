"""
Used with ble_demo_central.py. Receives Bluefruit LE ColorPackets from a central,
and updates a NeoPixel FeatherWing to show the history of the received packets.
"""

import board
import neopixel

import adafruit_ble
from adafruit_ble.services.nordic import UARTService
from adafruit_bluefruit_connect.packet import Packet
# Only the packet classes that are imported will be known to Packet.
from adafruit_bluefruit_connect.color_packet import ColorPacket

# This hasn't been updated.

NUM_PIXELS = 32
np = neopixel.NeoPixel(board.D10, NUM_PIXELS, brightness=0.1)
next_pixel = 0

def mod(i):
    """Wrap i to modulus NUM_PIXELS."""
    return i % NUM_PIXELS

adafruit_ble.add_local_service(UARTService)
adafruit_ble.advertise(UARTService)
while True:
    for peer in adafruit_ble.peers:
        packet = Packet.from_stream(peer.local.uart)
        if isinstance(packet, ColorPacket):
            print(packet.color)
            np[next_pixel] = packet.color
            np[mod(next_pixel + 1)] = (0, 0, 0)
        next_pixel = (next_pixel + 1) % NUM_PIXELS
