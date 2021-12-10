from tkinter import *


class Sensor1(Toplevel):
    def __init__(self, num):
        Toplevel.__init__(self)
        self.x = 10
        self.geometry("650x650+100+100")
        self.title("Sensor" + str(num) +  " reszletes adatok")
        self.resizable(False, False)
