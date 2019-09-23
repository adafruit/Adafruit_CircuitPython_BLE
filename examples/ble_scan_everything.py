from adafruit_ble import SmartAdapter

adapter = SmartAdapter()
print("scanning")
found = set()
for entry in adapter.start_scan(timeout=60, minimum_rssi=-80):
    addr = entry.address
    if addr not in found:
        print(entry)
    found.add(addr)

print("scan done")
