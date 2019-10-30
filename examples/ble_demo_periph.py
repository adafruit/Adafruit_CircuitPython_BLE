"""
Used with ble_demo_central.py. Receives Bluefruit LE ColorPackets from a central,
and updates a NeoPixel FeatherWing to show the history of the received packets.
"""

import board
import neopixel

from adafruit_ble import SmartAdapter
from adafruit_ble.advertising.standard import ProvideServiceAdvertisement
from adafruit_ble.services.nordic import UARTService

# Only the packet classes that are imported will be known to Packet.
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.color_packet import ColorPacket

NUM_PIXELS = 32
np = neopixel.NeoPixel(board.D10, NUM_PIXELS, brightness=0.1)
next_pixel = 0

def mod(i):
    """Wrap i to modulus NUM_PIXELS."""
    return i % NUM_PIXELS


adapter = SmartAdapter()
uart = UARTService()
advertisement = ProvideServiceAdvertisement(uart)

while True:
    adapter.start_advertising(advertisement)
    while not adapter.connected:
        pass
    while adapter.connected:
        packet = Packet.from_stream(uart)
        if isinstance(packet, ColorPacket):
            print(packet.color)
            np[next_pixel] = packet.color
            np[mod(next_pixel + 1)] = (0, 0, 0)
        next_pixel = (next_pixel + 1) % NUM_PIXELS
