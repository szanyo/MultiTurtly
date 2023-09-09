from graphics.Box import Box
from graphics.TextBox import TextBox


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
        self._elements["LBOX"].Radius = 20
        self._elements["LBOX"].PaintColor = "white"

        # Right box
        self._elements["RBOX"] = Box()
        self._elements["RBOX"].Radius = 20
        self._elements["RBOX"].PaintColor = "white"
        self._elements["RBOX"].Margin = 10

        # Right box elements

        self._right_box_elements_number = 10
        for i in range(self._right_box_elements_number):
            self._elements["RBOX_E" + str(i)] = TextBox()
            self._elements["RBOX_E" + str(i)].PaintColor = "yellow"
            self._elements["RBOX_E" + str(i)].TextColor = "white"
            self._elements["RBOX_E" + str(i)].Text = f"{i}: Árvíztűrő tükörfúrógép "
            self._elements["RBOX_E" + str(i)].FontSize = 3*i+1
            self._elements["RBOX_E" + str(i)].Radius = 20
            self._elements["RBOX_E" + str(i)].ShowBorder = True

        # Calculated values that depend on the constants and the window size
        self._calculate()

    def update(self):
        self._calculate()

    def _calculate(self):
        # Update window size
        self._elements["WIDTH"] = self._graphics.Window.window_width()
        self._elements["HEIGHT"] = self._graphics.Window.window_height()

        # Update Left box
        self._elements["LBOX"].Width = (self._elements["WIDTH"] - 3 * self._elements["MARGIN"]) * (2 / 3)
        self._elements["LBOX"].Height = self._elements["HEIGHT"] - 2 * self._elements["MARGIN"]

        self._elements["LBOX"].X = (
                self._elements["MARGIN"] - self._elements["WIDTH"] / 2 + self._elements["LBOX"].Width / 2)
        self._elements["LBOX"].Y = 0

        # Update Right box
        self._elements["RBOX"].Width = self._elements["WIDTH"] - 3 * self._elements["MARGIN"] - self._elements[
            "LBOX"].Width
        self._elements["RBOX"].Height = self._elements["HEIGHT"] - 2 * self._elements["MARGIN"]

        self._elements["RBOX"].X = (
                self._elements["WIDTH"] / 2 - self._elements["MARGIN"] - self._elements["RBOX"].Width / 2)
        self._elements["RBOX"].Y = 0

        # Update Right box elements (TextBoxes)
        sample_width = self._elements["RBOX"].Width - 2 * self._elements["RBOX"].Margin
        sample_height = (self._elements["RBOX"].Height - (self._right_box_elements_number + 1) * self._elements[
            "RBOX"].Margin) / self._right_box_elements_number
        base_y = self._elements["RBOX"].Y + self._elements["RBOX"].Height / 2 - self._elements["RBOX"].Margin

        for i in range(self._right_box_elements_number):
            self._elements["RBOX_E" + str(i)].Width = sample_width
            self._elements["RBOX_E" + str(i)].Height = sample_height

            self._elements["RBOX_E" + str(i)].X = self._elements["RBOX"].X
            self._elements["RBOX_E" + str(i)].Y = base_y - sample_height / 2 - i * (
                        sample_height + self._elements["RBOX"].Margin)

    def paint(self):
        self._elements["LBOX"].paint()
        self._elements["RBOX"].paint()
        for i in range(self._right_box_elements_number):
            self._elements["RBOX_E" + str(i)].paint()

    def getElement(self, name):
        return self._elements[name]
