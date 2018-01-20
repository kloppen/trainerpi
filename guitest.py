from tkinter import *
from random import random

class App:

    def __init__(self, master):

        frame = Frame(master)
        frame.pack()

        font = ("Helvetica", 16)

        self.speed = Label(frame, height=2, justify="left", font=font)
        self.speed.pack()

        self.cadence = Label(frame, height=2, justify="left", font=font)
        self.cadence.pack()

        self.power = Label(frame, height=2, justify="left", font=font)
        self.power.pack()

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.update_values()

    def update_values(self):
        self.speed.config(text="Speed: {} km/h".format(random()))
        self.cadence.config(text="Cadence: {} RPM".format(random()))
        self.power.config(text="Power: {} W".format(random()))
        self.speed.after(200, self.update_values)

    def say_hi(self):
        print("hi there, everyone!")


root = Tk()
app = App(root)
root.mainloop()