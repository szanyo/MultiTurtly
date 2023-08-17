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
        self._empty_movement_thread = None
        self._map = Box()
        self._turtle_instance = Turtle()
        self._turtle_color = kwargs.get(TurtlyDataKeys.PLAYER_COLOR.value,
                                        (randint(0, 255), randint(0, 255), randint(0, 255)))
        self._turtle_initial_position = kwargs.get(TurtlyDataKeys.PLAYER_INITIAL_POSITION.value,
                                                   (randint(0, 2), randint(0, 2)))
        self._turtle_initial_direction = kwargs.get(TurtlyDataKeys.PLAYER_INITIAL_DIRECTION.value, 0)
        self.movement_queue = Queue()
        self.history = History()

    def updateTurtle(self):
        self.updateWindowSize()

        self._turtle_instance = Turtle(visible=False)
        self._turtle_instance.speed(0)
        self._turtle_instance.color(self._turtle_color)
        self._turtle_instance.shape("turtle")
        self._turtle_instance.shapesize(stretch_wid=1.5)
        self._turtle_instance.up()
        self._turtle_instance.showturtle()
        self._turtle_instance.goto(self._map.x, self._map.y)
        self._turtle_instance.setheading(90)
        self._turtle_instance.down()

        self.redrawHistory()

    def empty_movement_loop(self):
        while True:
            self.empty_movement_queue()
            time.sleep(0.1)

    def empty_movement_queue(self):
        while not self.movement_queue.empty():
            movement = self.movement_queue.get()
            movement()
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

    def _right(self):
        print("right")
        self._turtle_instance.pendown()
        angle = 45
        self._direction -= angle
        self._direction %= 360
        self._turtle_instance.right(angle)

    def _forward(self):
        print(f"forward: {self._unit}")
        self._turtle_instance.pendown()
        future_moving_unit = self._unit if (self._direction % 90 == 0) else self._unit * pow(2, 0.5)

        # TODO? WRONG
        future_x = self._turtle_instance.xcor() + future_moving_unit * cos(radians(self._direction))
        future_y = self._turtle_instance.ycor() + future_moving_unit * sin(radians(self._direction))

        boundary_x = self._map.x + 2 * self._unit
        boundary_neg_x = self._map.x - 2 * self._unit
        boundary_y = self._map.y + 2 * self._unit
        boundary_neg_y = self._map.y - 2 * self._unit

        print(f"boundaries: {boundary_neg_x}, {boundary_x}, {boundary_neg_y}, {boundary_y}")
        print(f"future position: {future_x}, {future_y}")

        if boundary_neg_x < future_x < boundary_x and boundary_neg_y < future_y < boundary_y:
            self._turtle_instance.forward(future_moving_unit)
            print(f"new position: {self._turtle_instance.position()}")
        else:
            print("Out of bounds")

    def updateWindowSize(self):
        self._map = Graphics().GUI.getElement("LBOX")
        self._half_width = (self._map.width / 2) * 0.9
        self._half_height = (self._map.height / 2) * 0.9

        unit_width = self._half_width / 2

        unit_height = self._half_height / 2

        self._unit = unit_width if unit_width < unit_height else unit_height
