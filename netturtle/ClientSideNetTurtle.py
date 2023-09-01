import time
from math import radians, cos, sin
from queue import Queue
from random import randint
from turtle import Turtle, tracer

from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.patterns.History import History
from graphics.Box import Box
from graphics.Graphics import Graphics, GraphicsCommands
from netturtle.AbstractNetTurtle import AbstractNetTurtle

DEFAULT_COLOR_TUPLE = (125, 125, 125)


class ClientSideNetTurtle(AbstractNetTurtle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._boundary_x = 0
        self._boundary_neg_x = 0
        self._boundary_y = 0
        self._boundary_neg_y = 0
        self._stretch_wid = 1.5

        self._empty_movement_thread = None
        self._map = Box()
        self._turtle_instance = Turtle()
        self._turtle_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self._turtle_initial_position = (randint(0, 2), randint(0, 2))
        self._turtle_initial_direction = 90
        self._direction = self._turtle_initial_direction
        self.movement_queue = Queue()
        self.history = History()

    def updateTurtle(self):
        self.updateWindowSize()

        self._turtle_instance = Turtle(visible=False)
        self._turtle_instance.speed(0)
        self._turtle_instance.color(self._turtle_color)
        self._turtle_instance.shape("turtle")
        self._turtle_instance.shapesize(stretch_wid=self._stretch_wid)
        self._turtle_instance.up()
        self._turtle_instance.showturtle()
        self._turtle_instance.setheading(self._turtle_initial_direction)
        self._direction = self._turtle_initial_direction
        self._turtle_instance.goto(self._map.X + self._turtle_initial_position[0] * self._unit, self._map.Y + self._turtle_initial_position[1] * self._unit)
        self._turtle_instance.down()

        self.redrawHistory()

    def empty_movement_loop(self):
        while True:
            self.empty_movement_queue()
            time.sleep(0.1)

    def empty_movement_queue(self):
        while not self.movement_queue.empty():
            movement = self.movement_queue.get()
            if movement():
                self.history.add(movement)

    def redrawHistory(self):
        history = self.history.get()
        tracer(False)
        for movement in history:
            movement()
        tracer(True)

    def turn_left(self):
        self.movement_queue.put(lambda: self._left())

    def turn_right(self):
        self.movement_queue.put(lambda: self._right())

    def move_forward(self):
        self.movement_queue.put(lambda: self._forward())

    def _left(self):
        print("left")
        self._turtle_instance.pendown()
        angle = 45
        self._direction += angle
        self._direction %= 360
        self._turtle_instance.left(angle)
        return True

    def _right(self):
        print("right")
        self._turtle_instance.pendown()
        angle = 45
        self._direction -= angle
        self._direction %= 360
        self._turtle_instance.right(angle)
        return True

    def _forward(self):
        print(f"forward: {self._unit}")
        self._turtle_instance.pendown()
        future_moving_unit = self._unit if (self._direction % 90 == 0) else self._unit * pow(2, 0.5)

        future_x = round(self._turtle_instance.xcor() + future_moving_unit * cos(radians(self._direction)), 2)
        future_y = round(self._turtle_instance.ycor() + future_moving_unit * sin(radians(self._direction)), 2)

        # print(f"boundaries: {self._boundary_neg_x}, {self._boundary_x}, {self._boundary_neg_y}, {self._boundary_y}")
        # print(f"direction: {self._direction}")
        # print(f"heading: {self._turtle_instance.heading()}")
        # print(f"future position: {future_x}, {future_y}")

        if self._boundary_neg_x <= future_x <= self._boundary_x and self._boundary_neg_y <= future_y <= self._boundary_y:
            self._turtle_instance.forward(future_moving_unit)
            # print(f"new position: {self._turtle_instance.position()}")
            return True
        else:
            print("Warning: Try to move out of the map!")
            return False

    def updateWindowSize(self):
        self._map = Graphics().GUI.getElement("LBOX")
        self._half_width = (self._map.Width / 2) * 0.9
        self._half_height = (self._map.Height / 2) * 0.9

        unit_width = self._half_width / 2

        unit_height = self._half_height / 2

        self._unit = unit_width if unit_width < unit_height else unit_height

        self._boundary_x = round(self._map.X + 2 * self._unit, 2)
        self._boundary_neg_x = round(self._map.X - 2 * self._unit, 2)
        self._boundary_y = round(self._map.Y + 2 * self._unit, 2)
        self._boundary_neg_y = round(self._map.Y - 2 * self._unit, 2)

        self._stretch_wid = self._unit / 75
        if self._stretch_wid < 1.5:
            self._stretch_wid = 1.5
