from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import collections
import time


class CSCMeasurement:
    """
    Defines the fields of a CSC measurement
    """
    def __init__(self):
        self.wheel_revolution_data_present = False
        self.crank_revolution_data_present = False
        self.wheel_revs = 0
        self.wheel_event_time = 0
        self.crank_revs = 0
        self.crank_event_time = 0
        self.time = 0.

    def from_bytes(self, measurement: bytes) -> None:
        """
        Parses the raw bytes that the sensor provides
        :param measurement: The raw bytes provided by the sensor
        :return:
        """
        self.time = time.time()
        flags = measurement[0]
        self.wheel_revolution_data_present = bool(flags & (1 << 0))
        self.crank_revolution_data_present = bool(flags & (1 << 1))

        if self.wheel_revolution_data_present:
            data = struct.unpack("<BLH", measurement)
            self.wheel_revs = data[1]
            self.wheel_event_time = data[2]
        elif self.crank_revolution_data_present:
            data = struct.unpack("<BHH", measurement)
            self.crank_revs = data[1]
            self.crank_event_time = data[2]


def meas_difference(t1: int, t2: int, bits: int) -> float:
    """
    Determines the difference between two measurements
    :param t1: The first measurement
    :param t2: The second measurement
    :param bits: The number of bits for the measurement (when it wraps around to zero)
    :return: The difference between the two
    """
    if t2 < t1:
        # It wrapped around 2**bits
        return ((1 << bits) - 1) - t1 + t2
    return t2 - t1


AVERAGE_LENGTH = 10


class CSCDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self._prev_meas = collections.deque(maxlen=AVERAGE_LENGTH)
        self._last_measurement = None
        self.notification_callback = None

    def handleNotification(self, cHandle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)
        if self._last_measurement is not None:
            meas_diff = CSCMeasurement()
            meas_diff.crank_revolution_data_present = meas.crank_revolution_data_present
            meas_diff.wheel_revolution_data_present = meas.wheel_revolution_data_present
            meas_diff.wheel_revs = meas_difference(self._last_measurement.wheel_revs, meas.wheel_revs, 32)
            meas_diff.crank_revs = meas_difference(self._last_measurement.crank_revs, meas.crank_revs, 16)
            meas_diff.wheel_event_time = meas_difference(self._last_measurement.wheel_event_time,
                                                         meas.wheel_event_time,
                                                         16) / 1024
            meas_diff.crank_event_time = meas_difference(self._last_measurement.wheel_event_time,
                                                         meas.crank_event_time,
                                                         16) / 1024
            meas_diff.time = meas.time - self._last_measurement.time
            self._prev_meas.append(meas_diff)
        self._last_measurement = meas

        if len(self._prev_meas) > 2:
            if meas.wheel_revolution_data_present:
                avg = sum([m.wheel_revs for m in self._prev_meas]) / sum([m.time for m in self._prev_meas])
                self.notification_callback(avg, 0.)
            if meas.crank_revolution_data_present:
                avg = sum([m.crank_revs for m in self._prev_meas]) / sum([m.time for m in self._prev_meas])
                self.notification_callback(0., avg)


csc_service_uuid = UUID(0x1816)
csc_char_uuid = UUID(0x2A5B)
location_char_uuid = UUID(0x2A5D)


class CSCSensor:
    """
    This class defines a cycling speed and cadence sensor
    """

    def __init__(self, address: str, notification_callback: function):
        """
        Initializes the class
        :param address: A string with the address of the sensor
        :param notification_callback: A function that takes two floats (speed, cadence) that will be called for each
            notification
        """
        self.peripheral = Peripheral(address, "random")
        delegate = CSCDelegate()
        delegate.notification_callback = notification_callback
        self.peripheral.setDelegate(delegate)
        self.cscService = self.peripheral.getServiceByUUID(csc_service_uuid)
        self.cscCharacteristic = self.cscService.getCharacteristics(csc_char_uuid)[0]
        self.cscCharacteristicHandle = self.cscCharacteristic.getHandle()

    def get_location(self) -> str:
        """
        Returns the location of the sensor
        :return: an integer representing the location
        """
        location_list = ["Other",
                         "Top of shoe",
                         "In shoe",
                         "Hip",
                         "Front Wheel",
                         "Left Crank",
                         "Right Crank",
                         "Left Pedal",
                         "Right Pedal",
                         "Front Hub",
                         "Rear Dropout",
                         "Chainstay",
                         "Rear Wheel",
                         "Rear Hub",
                         "Chest",
                         "Spider",
                         "Chain Ring"]
        characteristic = self.cscService.getCharacteristics(location_char_uuid)[0]
        handle = characteristic.getHandle()
        location = self.peripheral.readCharacteristic(handle)
        return location_list[int.from_bytes(location, "little")]

    def notifications(self, notify: bool) -> None:
        """
        Starts or stops notifications from this sensor
        :param notify: True to start notifications, False to stop
        :return: None
        """
        hccc = 0
        for descriptor in self.peripheral.getDescriptors(self.cscCharacteristicHandle):
            if descriptor.uuid == 0x2902:
                hccc = descriptor.handle
                break

        self.peripheral.writeCharacteristic(hccc, struct.pack("<bb", 0x01 & notify, 0x00))

    def wait_for_notifications(self, time: float) -> bool:
        """
        Wait `time` seconds for a notification
        :param time: The number of seconds to wait
        :return: A boolean indicating whether a notification was received
        """
        return self.peripheral.waitForNotifications(time)
