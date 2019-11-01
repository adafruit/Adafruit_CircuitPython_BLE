"""
This demo uses advertising to set the color of scanning devices depending on the strongest broadcast
signal received. Circuit Playgrounds can be switched between advertising and scanning using the
slide switch. The buttons change the color when advertising.
"""

import time
import board
import neopixel
import digitalio

from adafruit_ble import BLERadio
from adafruit_ble.advertising.adafruit import AdafruitColor

# The color pickers will cycle through this list with buttons A and B.
color_options = [0x110000,
                 0x111100,
                 0x001100,
                 0x001111,
                 0x000011,
                 0x110011,
                 0x111111,
                 0x111111,
                 0x0,
                 0x0]

ble = BLERadio()

slide_switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
slide_switch.pull = digitalio.Pull.UP
button_a = digitalio.DigitalInOut(board.BUTTON_A)
button_a.pull = digitalio.Pull.DOWN
button_b = digitalio.DigitalInOut(board.BUTTON_B)
button_b.pull = digitalio.Pull.DOWN

led = digitalio.DigitalInOut(board.D13)
led.switch_to_output()

neopixels = neopixel.NeoPixel(board.NEOPIXEL, 10)

i = 0
advertisement = AdafruitColor()
advertisement.color = color_options[i]
neopixels.fill(color_options[i])
while True:
    # The first mode is the color selector which broadcasts it's current color to other devices.
    if slide_switch.value:
        print("Broadcasting color")
        ble.start_advertising(advertisement)
        while slide_switch.value:
            last_i = i
            if button_a.value:
                i += 1
            if button_b.value:
                i -= 1
            i %= len(color_options)
            if last_i != i:
                color = color_options[i]
                neopixels.fill(color)
                print("New color {:06x}".format(color))
                advertisement.color = color
                ble.stop_advertising()
                ble.start_advertising(advertisement)
                time.sleep(0.5)
        ble.stop_advertising()
    # The second mode listens for color broadcasts and shows the color of the strongest signal.
    else:
        closest = None
        closest_rssi = -80
        closest_last_time = 0
        print("Scanning for colors")
        while not slide_switch.value:
            for entry in ble.start_scan(AdafruitColor, minimum_rssi=-80, timeout=1):
                if slide_switch.value:
                    break
                now = time.monotonic()
                new = False
                if entry.address == closest:
                    pass
                elif entry.rssi > closest_rssi or now - closest_last_time > 0.4:
                    closest = entry.address
                else:
                    continue
                closest_rssi = entry.rssi
                closest_last_time = now
                neopixels.fill(entry.color)
        ble.stop_scan()
