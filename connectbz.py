from bluezero import central
from time import sleep


class CSC:
    def __init__(self, device_addr, adapter_addr=None):
        self.csc = central.Central(adapter_addr=adapter_addr,
                                   device_addr=device_addr)

    def connect(self):
        self.csc.connect()
        while not self.csc.services_resolved:
            sleep(0.5)
        self.csc.load_gatt()

    def disconnect(self):
        self.csc.disconnect()


csc1 = CSC(adapter_addr="B8:27:EB:3E:E3:51",
                       device_addr="D0:AC:A5:BF:B7:52")
csc1.connect()

csc1.disconnect()

