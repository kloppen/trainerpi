from bluepy.btle import UUID, Peripheral, DefaultDelegate
import struct
import time
from typing import Callable
import asyncio


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


class SpeedAveragingSegment:
    """
    This class is used for speed averaging. Each "segment" is the period between subsequent changes in the rotation
    count provided by the sensor.

    A window is a period of time that contains part or all of one or more segment.
    """
    def __init__(self, t_start_ticks: int, n_start: int):
        self.t_start_ticks = t_start_ticks
        self.t_end_ticks = None
        self.n_start = n_start
        self.n_end = None

    def set_finish(self, t_end_ticks, n_end):
        self.t_end_ticks = t_end_ticks
        self.n_end = n_end

    @property
    def ticks_total(self) -> float:
        return self.t_end_ticks - self.t_start_ticks

    @property
    def rotation_speed(self) -> float:
        return (self.n_end - self.n_start) / (self.t_end_ticks - self.t_start_ticks)

    def ticks_within_window(self, window_start: float, window_end: float) -> float:
        if self.rotation_speed is None:
            return 0.  # The segment is not yet complete
        return min(window_end, self.t_end_ticks) - max(window_start, self.t_start_ticks)


class SpeedAverager:
    def __init__(self, ticks_per_second: int, averaging_window: float, bits_t: int, bits_n: int):
        """
        This class provides the ability to average speed over a certain averaging window.

        Since the bluetooth CSC sensors provide integers for

        :param ticks_per_second: The number of ticks of the timer counter per second (1024, normally)
        :param bits_t: The number of bits that represents time
        :param bits_n: The number of bits that represents rotations
        :param averaging_window: The time over which to average the speed
        """
        self.speed_segments = []
        self.cur_speed_segment = None
        self.ticks_per_second = ticks_per_second
        self.averaging_window = averaging_window
        self.bits_t = bits_t
        self.bits_n = bits_n
        # Since the time and number of revolutions wraps around zero, we will store the smallest numbers that these
        # could be and wrap as necessary
        self.min_t_ticks = None
        self.min_n = None

    def update_average(self, cur_t_ticks: int, cur_n: int) -> float:
        if self.cur_speed_segment is None:
            self.cur_speed_segment = SpeedAveragingSegment(cur_t_ticks, cur_n)
            self.min_t_ticks = cur_t_ticks
            self.min_n = cur_n

        if self.cur_speed_segment.n_start != cur_n:
            while cur_t_ticks < self.min_t_ticks:
                cur_t_ticks += 2 ** self.bits_t

            while cur_n < self.min_n:
                cur_n += 2 ** self.bits_n

            self.min_t_ticks = cur_t_ticks
            self.min_n = cur_n

            self.cur_speed_segment.set_finish(cur_t_ticks, cur_n)
            self.speed_segments.append(self.cur_speed_segment)
            self.cur_speed_segment = SpeedAveragingSegment(cur_t_ticks, cur_n)

            self.speed_segments = list(
                [ss for ss in self.speed_segments
                 if ss.t_end_ticks >= cur_t_ticks / self.ticks_per_second - self.averaging_window
                 ])

            ticks_window = sum(
                [s.ticks_within_window(cur_t_ticks - self.averaging_window * self.ticks_per_second, cur_t_ticks)
                 for s in self.speed_segments]
            ) / self.ticks_per_second
            if ticks_window > 0:
                return sum(
                    [s.ticks_within_window(cur_t_ticks - self.averaging_window * self.ticks_per_second, cur_t_ticks) *
                     s.rotation_speed
                     for s in self.speed_segments if s.rotation_speed is not None]) / ticks_window
            return 0.  # The window contains no completed segments


class CSCDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
        self.notification_callback = None
        self.average_wheel = SpeedAverager(ticks_per_second=1024, averaging_window=3., bits_t=16, bits_n=32)
        self.average_crank = SpeedAverager(ticks_per_second=1024, averaging_window=3., bits_t=16, bits_n=16)

    def handleNotification(self, cHandle, data):
        meas = CSCMeasurement()
        meas.from_bytes(data)

        if meas.crank_revolution_data_present:
            crank_speed = self.average_crank.update_average(meas.crank_event_time, meas.crank_revs)
            self.notification_callback(0., crank_speed)

        if meas.wheel_revolution_data_present:
            wheel_speed = self.average_wheel.update_average(meas.wheel_event_time, meas.wheel_revs)
            self.notification_callback(wheel_speed, 0.)


CSC_SERVICE_UUID = UUID(0x1816)
CSC_CHAR_UUID = UUID(0x2A5B)
LOCATION_CHAR_UUID = UUID(0x2A5D)


class CSCSensor:
    """
    This class defines a cycling speed and cadence sensor
    """

    def __init__(self):
        self.peripheral = None
        self.cscService = None
        self.cscCharacteristic = None
        self.cscCharacteristicHandle = None

    def connect(self, address: str,
                notification_callback: Callable[[float, float], None]):
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
        self.cscService = self.peripheral.getServiceByUUID(CSC_SERVICE_UUID)
        self.cscCharacteristic = self.cscService.getCharacteristics(CSC_CHAR_UUID)[0]
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
        characteristic = self.cscService.getCharacteristics(LOCATION_CHAR_UUID)[0]
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

    @asyncio.coroutine
    async def wait_for_notifications(self, wait_time: float) -> bool:
        """
        Wait `wait_time` seconds for a notification
        :param wait_time: The number of seconds to wait
        :return: A boolean indicating whether a notification was received
        """
        return self.peripheral.waitForNotifications(wait_time)
