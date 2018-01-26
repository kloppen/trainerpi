import pygatt
from binascii import hexlify

adapter = pygatt.GATTToolBackend()

def handle_data(handle, value):
    print("Received data: {}".format(hexlify(value)))

try:
    adapter.start()
    device = adapter.connect("D0:AC:A5:BF:B7:52", timeout=20)
    
    device.subscribe("00002a5b-0000-1000-8000-00805f9b34fb",
            callback=handle_data)

finally:
    adapter.stop()

