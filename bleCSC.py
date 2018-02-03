from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import collections


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

    def from_bytes(self, measurement: bytes) -> None:
        """
        Parses the raw bytes that the sensor provides
        :param measurement: The raw bytes provided by the sensor
        :return:
        """
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

    def __eq__(self, other) -> bool:
        """Overrides the default implementation"""
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other) -> bool:
        """Overrids the default implementation"""
        return not self.__eq__(other)


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


class CSCDelegate(DefaultDelegate):
    def __init__(self, params):
        DefaultDelegate.__init__(self)
        self._prev_meas = collections.deque(maxlen=4)
        self._last_measurement = None

    def handleNotification(self, cHandle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)
        print("WR: {} LWT: {} CR: {} LCT: {} Handle: {}".format(
            meas.wheel_revs,
            meas.wheel_event_time,
            meas.crank_revs,
            meas.crank_event_time,
            cHandle
        ))
        if meas != self._last_measurement:
            meas_diff= CSCMeasurement()
            meas_diff.crank_revolution_data_present = meas.crank_revolution_data_present
            meas_diff.wheel_revolution_data_present = meas.wheel_revolution_data_present
            meas_diff.wheel_revs = meas_difference(meas.wheel_revs, self._last_measurement.wheel_revs, 32)
            meas_diff.crank_revs = meas_difference(meas.crank_revs, self._last_measurement.crank_revs, 16)
            meas_diff.wheel_event_time = meas_difference(meas.wheel_event_time,
                                                         self._last_measurement.wheel_event_time,
                                                         16)
            meas_diff.crank_event_time = meas_difference(meas.crank_event_time,
                                                         self._last_measurement.wheel_event_time,
                                                         16)
            self._prev_meas.append(meas)
        self._last_measurement = meas

        if len(self._prev_meas) == self._prev_meas.maxlen:
            avg = 0.
            if meas.wheel_revolution_data_present:
                avg = sum([m.wheel_revs / m.wheel_event_time for m in self._prev_meas]) / len(self._prev_meas)
            if meas.crank_revolution_data_present:
                avg = sum([m.crank_revs / m.crank_event_time for m in self._prev_meas]) / len(self._prev_meas)
            print("...Average speed: {} revs/s".format(avg))


csc_service_uuid = UUID(0x1816)
csc_char_uuid = UUID(0x2A5B)
location_char_uuid = UUID(0x2A5D)


class CSCSensor:
    """
    This class defines a cycling speed and cadence sensor
    """

    def __init__(self, address: str):
        """
        Initializes the class
        :param address: A string with the address of the sensor
        """
        self.peripheral = Peripheral(address, "random")
        self.peripheral.setDelegate(CSCDelegate(self.peripheral))  # TODO: Should allow user to set this
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
