from turtle import speed, isvisible, color, isdown, hideturtle, up, goto, down, fd, circle, showturtle

from graphics.Box import Box


class GUI:
    def __init__(self, graphics):
        self._graphics = graphics
        self._elements = {}
        self._initialize()

    def _initialize(self):
        # Constants
        self._elements["MARGIN"] = 20

        # GUI elements
        # Left box
        self._elements["LBOX"] = Box()
        self._elements["LBOX"]._radius = 20
        self._elements["LBOX"]._paintcolor = "white"

        # Right box
        self._elements["RBOX"] = Box()
        self._elements["RBOX"]._radius = 20
        self._elements["RBOX"]._paintcolor = "white"

        # Right box elements


        # Calculated values that depend on the constants and the window size
        self._calculate()

    def update(self):
        self._calculate()

    def _calculate(self):
        # Update window size
        self._elements["WIDTH"] = self._graphics.Window.window_width()
        self._elements["HEIGHT"] = self._graphics.Window.window_height()

        # Update Left box
        self._elements["LBOX"]._width = (self._elements["WIDTH"] - 3 * self._elements["MARGIN"]) * (2 / 3)
        self._elements["LBOX"]._height = self._elements["HEIGHT"] - 2 * self._elements["MARGIN"]

        self._elements["LBOX"]._x = (
                self._elements["MARGIN"] - self._elements["WIDTH"] / 2 + self._elements["LBOX"]._width / 2)
        self._elements["LBOX"]._y = 0

        # Update Right box
        self._elements["RBOX"]._width = self._elements["WIDTH"] - 3 * self._elements["MARGIN"] - self._elements["LBOX"]._width
        self._elements["RBOX"]._height = self._elements["HEIGHT"] - 2 * self._elements["MARGIN"]

        self._elements["RBOX"]._x = (
                self._elements["WIDTH"] / 2 - self._elements["MARGIN"] - self._elements["RBOX"]._width / 2)
        self._elements["RBOX"]._y = 0

    def paint(self):
        self._elements["LBOX"].paint()
        self._elements["RBOX"].paint()

    def getElement(self, name):
        return self._elements[name]
