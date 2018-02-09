import bleCSC
import numpy
import threading
import curses


ROLLING_LENGTH = 2096.  # mm
power_curve = numpy.loadtxt("power-4.csv", delimiter=",")


class CSCThread(threading.Thread):
    def __init__(self, group=None, name=None):
        threading.Thread.__init__(self, group=group, target=self.worker, name=name)
        self.address = ""
        self._number = 0
        self.stdscr = None
        self._location_row = 0
        self._data_row = 0

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, value):
        self._number = value
        n = 3
        self._location_row = n * value
        self._data_row = n * value + 1

    def handle_notification(self, wheel_speed: float, crank_speed: float) -> None:
        speed = wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
        power = numpy.interp(speed, power_curve[:, 0], power_curve[:, 1])
        self.stdscr.addstr(self._data_row, 0, "Wheel: {:2.0f} km/h, Power: {:3.0f} W, Crank: {:3.0f}".format(
            wheel_speed * 3600. * ROLLING_LENGTH / 1e+6,
            power,
            crank_speed * 60.
        ))
        self.stdscr.refresh()

    def worker(self):
        sensor = bleCSC.CSCSensor(self.address, self.handle_notification)
        location_wheel = sensor.get_location()
        self.stdscr.addstr(self._location_row, 0, "Location (wheel_sensor): {}".format(location_wheel))
        self.stdscr.refresh()
        sensor.notifications(True)
        while True:
            try:
                if sensor.wait_for_notifications(1.0):
                    continue
                self.stdscr.addstr(self._data_row, 0, "Waiting for Sensor {}...".format(self.number))
                self.stdscr.refresh()
            except (KeyboardInterrupt, SystemExit):
                break


def main_screen(stdscr):
    stdscr.clear()

    sensor1_thread = CSCThread()
    sensor1_thread.address = "D0:AC:A5:BF:B7:52"
    sensor1_thread.number = 1
    sensor1_thread.stdscr = stdscr

    sensor2_thread = CSCThread()
    sensor2_thread.address = "C6:F9:84:6A:C0:8E"
    sensor2_thread.number = 2
    sensor2_thread.stdscr = stdscr

    sensor1_thread.start()
    sensor2_thread.start()


curses.wrapper(main_screen)
