from adafruit_ble import SmartAdapter
from adafruit_ble.advertising.adafruit import AdafruitColor
import time
import board
import neopixel
import digitalio

# This should work but I didn't test after linting.

# The color pickers will cycle through this list with buttons A and B.
color_options = [0x110000, 0x111100, 0x001100, 0x001111, 0x000011, 0x110011, 0x111111, 0x111111, 0x0, 0x0]

class Stub:
    def __init__(self):
        self.value = False

adapter = SmartAdapter()
if hasattr(board, "SLIDE_SWITCH"):
    slide_switch = digitalio.DigitalInOut(board.SLIDE_SWITCH)
    slide_switch.pull = digitalio.Pull.UP
    button_a = digitalio.DigitalInOut(board.BUTTON_A)
    button_a.pull = digitalio.Pull.DOWN
    button_b = digitalio.DigitalInOut(board.BUTTON_B)
    button_b.pull = digitalio.Pull.DOWN
else:
    slide_switch = Stub()
    slide_switch.value = True
    button_a = Stub()
    button_a.value = True
    button_b = Stub()


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
        adapter.start_advertising(advertisement)
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
                print("new color {:06x}".format(color))
                advertisement.color = color
                adapter.stop_advertising()
                print(bytes(advertisement.manufacturer_data), repr(advertisement), bytes(advertisement))
                adapter.start_advertising(advertisement)
                time.sleep(0.5)
        adapter.stop_advertising()
    # The second mode listens for color broadcasts and shows the color of the strongest signal.
    else:
        closest = None
        closest_rssi = -80
        closest_last_time = 0
        for entry in adapter.start_scan([AdafruitColor], minimum_rssi=-80):
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
        adapter.stop_scan()
