import bleCSC
import numpy
import threading
# import curses


ROLLING_LENGTH = 2096.  # mm
power_curve = numpy.loadtxt("power-4.csv", delimiter=",")


class CSCThread(threading.Thread):
    def __init__(self, group=None, name=None):
        threading.Thread.__init__(self, group=group, target=self.worker, name=name)
        self.address = ""
        self.name = ""

    def handle_notification(self, wheel_speed: float, crank_speed: float) -> None:
        speed = wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
        power = numpy.interp(speed, power_curve[:, 0], power_curve[:, 1])
        print("Wheel: {:2.0f} km/h, Power: {:3.0f} W, Crank: {:3.0f}".format(
            wheel_speed * 3600. * ROLLING_LENGTH / 1e+6,
            power,
            crank_speed * 60.
        ))

    def worker(self):
        sensor = bleCSC.CSCSensor(self.address, self.handle_notification)
        location_wheel = sensor.get_location()
        print("Location (wheel_sensor): {}".format(location_wheel))
        sensor.notifications(True)
        while True:
            try:
                if sensor.wait_for_notifications(1.0):
                    continue
                print("Waiting for {}...".format(self.name))
            except (KeyboardInterrupt, SystemExit):
                break


# def main_screen(stdscr):
#     stdscr.clear()

sensor1_thread = CSCThread()
sensor1_thread.address = "D0:AC:A5:BF:B7:52"
sensor1_thread.name = "Sensor 1"

sensor2_thread = CSCThread()
sensor2_thread.address = "C6:F9:84:6A:C0:8E"
sensor2_thread.name = "Sensor 2"

sensor1_thread.start()
sensor2_thread.start()


# curses.wrapper(main_screen)
