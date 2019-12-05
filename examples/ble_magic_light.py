"""This demo connects to a magic light and has it do a color wheel."""
import adafruit_ble
import _bleio
import time
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.magic_light import MagicLightService

def find_connection():
    for connection in radio.connections:
        if MagicLightService not in connection:
            continue
        return connection, connection[MagicLightService]
    return None, None

# Start advertising before messing with the display so that we can connect immediately.
radio = adafruit_ble.BLERadio()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

active_connection, pixels = find_connection()
current_notification = None
app_icon_file = None
while True:
    if not active_connection:
        print("Scanning for Magic Light")
        for scan in radio.start_scan(ProvideServicesAdvertisement):
            if MagicLightService in scan.services:
                active_connection = radio.connect(scan)
                try:
                    pixels = active_connection[MagicLightService]
                except _bleio.ConnectionError:
                    print("disconnected")
                    continue
                break
        radio.stop_scan()

    i = 0
    while active_connection.connected:
        pixels[0] = wheel(i % 256)
        i += 1

    active_connection = None
