import threading
import time
from math import radians, cos, sin
from queue import Queue
from turtle import Turtle


class NetTurtle():
    def __init__(self, wnd):
        super().__init__()
        self._wnd = wnd
        self._t = Turtle()
        self._t.speed(0)
        self._t.color("green")
        self._t.shape("turtle")
        self._t.shapesize(stretch_wid=1.5)
        self._t.goto(0, 0)
        self._t.pendown()
        self.movement_queue = Queue()
        self._empty_movement_thread = threading.Thread(target=self._empty_movement_queue)
        self._empty_movement_thread.start()
        self._direction = 0

        self._half_width = 0
        self._half_height = 0
        self._unit = 0

    def _empty_movement_queue(self):
        while True:
            while not self.movement_queue.empty():
                self.movement_queue.get()()
            time.sleep(0.1)

    def turn_left(self):
        self.movement_queue.put(lambda: self._left())

    def turn_right(self):
        self.movement_queue.put(lambda: self._right())

    def forward(self):
        self.movement_queue.put(lambda: self._forward())

    def _left(self):
        angle = 45
        self._direction += angle
        self._direction %= 360
        self._t.left(angle)

    def _right(self):
        angle = 45
        self._direction -= angle
        self._direction %= 360
        self._t.right(angle)

    def _forward(self):
        print(self._unit)
        future_moving_unit = self._unit if (self._direction % 90 == 0) else self._unit * pow(2, 0.5)
        future_x = self._t.xcor() + future_moving_unit * cos(radians(self._direction))
        future_y = self._t.ycor() + future_moving_unit * sin(radians(self._direction))

        print(f"direction: {self._direction}")
        print(f"future_moving_unit: {future_moving_unit}")
        print(f"future_x: {future_x} half_width: {self._half_width}")
        print(f"future_y: {future_y} half_height: {self._half_height}")

        if self._half_width > future_x > -self._half_width and self._half_height > future_y > -self._half_height:
            self._t.forward(future_moving_unit)

        print(f"current_x: {self._t.xcor()}")
        print(f"current_y: {self._t.ycor()}")

    def updateWindowSize(self):
        self._half_width = self._wnd.window_width() / 2
        self._half_height = self._wnd.window_height() / 2

        # search largest integer modolus of self._half_width, but smaller than self._half_width
        # to get the first unit
        unit_width = 0
        for i in range(int(self._half_width / 2), 0, -1):
            if self._half_width % i == 0:
                unit_width = i
                break

        # search largest integer modolus of self._half_height, but smaller than self._half_height
        # to get the first unit
        unit_height = 0
        for i in range(int(self._half_height / 2), 0, -1):
            if self._half_height % i == 0:
                unit_height = i
                break

        self._unit = unit_width if unit_width < unit_height else unit_height
