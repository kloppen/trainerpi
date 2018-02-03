from bluezero import central
from bluezero import tools
from time import sleep
from binascii import hexlify
import asyncio
import aioblescan


class CSC:
    def __init__(self, device_addr, *, adapter_addr=None):
        self.csc = central.Central(adapter_addr=adapter_addr,
                                   device_addr=device_addr)

        self.csc_service_uuid = "00001816-0000-1000-8000-00805f9b34fb"
        self.csc_measurement_uuid = "00002a5b-0000-1000-8000-00805f9b34fb"

    def connect(self):
        self.csc.connect()
        while not self.csc.services_resolved:
            sleep(0.5)
        self.csc.load_gatt()

        self._csc_measurement = self.csc.add_characteristic(
                self.csc_service_uuid, self.csc_measurement_uuid)

    def subscribe_measurement(self, measurement_cb):
        self._csc_measurement.resolve_gatt()
        self._csc_measurement.add_characteristic_cb(measurement_cb)
        self._csc_measurement.start_notify()

    def disconnect(self):
        self.csc.disconnect()


def meas_cb(*args, **kwargs):
    print(args, kwargs)
    return True


csc1 = CSC(adapter_addr="B8:27:EB:3E:E3:51",
           device_addr="D0:AC:A5:BF:B7:52")

csc1.connect()
csc1.subscribe_measurement(meas_cb)

event_loop = asyncio.get_event_loop()


csc1.disconnect()

