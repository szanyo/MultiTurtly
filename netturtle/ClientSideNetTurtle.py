import time
from math import radians, cos, sin
from queue import Queue
from random import randint
from turtle import Turtle, tracer

from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.patterns.History import History
from graphics.Graphics import Graphics, GraphicsCommands
from netturtle.AbstractNetTurtle import AbstractNetTurtle

DEFAULT_COLOR_TUPLE = (125, 125, 125)


class ClientSideNetTurtle(AbstractNetTurtle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._empty_movement_thread = None
        self._wnd = Graphics().Window
        self._turtle_instance = Turtle()
        self._turtle_color = kwargs.get(TurtlyDataKeys.PLAYER_COLOR.value,
                                        (randint(0, 255), randint(0, 255), randint(0, 255)))
        self._turtle_initial_position = kwargs.get(TurtlyDataKeys.PLAYER_INITIAL_POSITION.value, (0, 0))
        self._turtle_initial_direction = kwargs.get(TurtlyDataKeys.PLAYER_INITIAL_DIRECTION.value, 0)
        self.movement_queue = Queue()
        self.history = History()

    def updateTurtle(self):
        self._turtle_instance = Turtle(visible=False)
        self._turtle_instance.speed(0)
        self._turtle_instance.color(self._turtle_color)
        self._turtle_instance.shape("turtle")
        self._turtle_instance.shapesize(stretch_wid=1.5)
        self._turtle_instance.up()
        self._turtle_instance.showturtle()
        x, y = Graphics().GUI.getElement("LBOX").x, Graphics().GUI.getElement("LBOX").y
        self._turtle_instance.goto(x, y)
        self._turtle_instance.setheading(90)
        self._turtle_instance.down()

        self.updateWindowSize()

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
        # future_x = self._turtle_instance.xcor() + future_moving_unit * cos(radians(self._direction))
        # future_y = self._turtle_instance.ycor() + future_moving_unit * sin(radians(self._direction))

        # if self._half_width > future_x > -self._half_width and self._half_height > future_y > -self._half_height:
        self._turtle_instance.forward(future_moving_unit)

    def updateWindowSize(self):
        # self._half_width = self._wnd.window_width() / 2
        # self._half_height = self._wnd.window_height() / 2
        #
        # # search largest integer modolus of self._half_width, but smaller than self._half_width
        # # to get the first unit
        # unit_width = 0
        # for i in range(int(self._half_width / 2), 0, -1):
        #     if self._half_width % i == 0:
        #         unit_width = i
        #         break
        #
        # # search largest integer modolus of self._half_height, but smaller than self._half_height
        # # to get the first unit
        # unit_height = 0
        # for i in range(int(self._half_height / 2), 0, -1):
        #     if self._half_height % i == 0:
        #         unit_height = i
        #         break
        #
        # self._unit = unit_width if unit_width < unit_height else unit_height

        self._unit = 20
