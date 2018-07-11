import bleCSC
import numpy
import asyncio
import pygame
import os
import collections


# --------------------------------------------------------------------------- #
#  SETTINGS                                                                   #
# --------------------------------------------------------------------------- #
ROLLING_LENGTH = 2096.  # mm
POWER_CURVE = numpy.loadtxt("power-4.csv", delimiter=",")
SCREEN_SIZE = WIDTH, HEIGHT = 320, 240
BORDER = 10
FONT_NAME = "DejaVuSans"
FONT_SIZE = 28
SCREEN_UPDATE_DELAY = 0.5
CSC_SENSOR_ADDRESSES = (
    "D0:AC:A5:BF:B7:52",
    "C6:F9:84:6A:C0:8E"
)


display_column = collections.namedtuple("display_column", ("title", "data"))
SIGNAL_EXIT = False


class TrainerThread:
    def __init__(self):
        self.display_row = None
        self.display_column_list = []


class CSCTrainer(TrainerThread):
    def __init__(self, address: str, display_row: int):
        super().__init__()
        self.address = address
        self.display_row = display_row
        self._location = ""

    def handle_notification(self, wheel_speed: float, crank_speed: float) -> None:
        speed = wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
        power = numpy.interp(speed, POWER_CURVE[:, 0], POWER_CURVE[:, 1])
        if "Wheel" in self._location:
            self.display_column_list = [
                display_column(
                    self._location,
                    "{:2.0f} km/h".format(
                        wheel_speed * 3600. * ROLLING_LENGTH / 1e+6
                    )
                ),
                display_column(
                    "",
                    "{:3.0f} W".format(power)
                )
            ]

        if "Crank" in self._location:
            self.display_column_list= [
                display_column(
                    self._location,
                    "{:3.0f} RPM".format(
                        crank_speed * 60.
                    )
                )
            ]

    async def worker(self):
        global SIGNAL_EXIT

        self.display_column_list = [
            display_column("Waiting for Sensor:", self.address)
        ]

        sensor = bleCSC.CSCSensor()
        sensor.connect(self.address, self.handle_notification)
        await asyncio.sleep(0)
        self._location = sensor.get_location()
        await asyncio.sleep(0)
        sensor.notifications(True)
        while True:
            if SIGNAL_EXIT:
                break
            try:
                await asyncio.sleep(0.01)
                notify_ret = await sensor.wait_for_notifications(1.0)
                if notify_ret:
                    continue
                self.display_column_list = [
                    display_column("Waiting for Sensor:", self.address)
                ]
            except (KeyboardInterrupt, SystemExit):
                break


class ScreenUpdateTrainer(TrainerThread):
    def __init__(self, thread_list):
        super().__init__()
        self.thread_list = thread_list
        os.putenv("SDL_FBDEV", "/dev/fb1")
        pygame.init()
        pygame.mouse.set_visible(False)
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)

    async def worker(self):
        global SIGNAL_EXIT
        while not SIGNAL_EXIT:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    SIGNAL_EXIT = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    SIGNAL_EXIT = True

            self.screen.fill((0, 0, 0))

            for thread in self.thread_list:
                if thread.display_row is not None:
                    for col_num, col_data in enumerate(thread.display_column_list):
                        self.draw_segment((col_num, thread.display_row), col_data.title, col_data.data, (255, 255, 255))

            pygame.display.flip()
            asyncio.sleep(SCREEN_UPDATE_DELAY)

    def draw_segment(self, seg: tuple, title: str, data: str, color: tuple):
        seg_width = WIDTH // 2
        seg_height = HEIGHT // 3
        x0 = seg_width * seg[0] + BORDER
        y0 = seg_height * seg[1] + BORDER
        x1 = seg_width * (seg[0] + 1) - BORDER
        y1 = seg_height * (seg[1] + 1) - BORDER

        title_text = self.font.render(title, True, color)
        self.screen.blit(title_text, (x0, y0))

        data_text = self.font.render(data, True, color)
        self.screen.blit(data_text, (x1 - data_text.get_width(), y1 - data_text.get_height()))


def run_trainer():
    all_threads = list(
        [CSCTrainer(address, i + 1) for (i, address) in enumerate(CSC_SENSOR_ADDRESSES)]
    )
    all_threads.append(ScreenUpdateTrainer(all_threads))

    # TODO: Add a worker for the time

    io_loop = asyncio.get_event_loop()
    tasks = list(
        [io_loop.create_task(thread.worker()) for thread in all_threads]
    )
    wait_tasks = asyncio.wait(tasks)
    io_loop.run_until_complete(wait_tasks)
    io_loop.close()


if __name__ == "__main__":
    run_trainer()
