from abc import ABC
from turtle import Turtle


class AbstractNetTurtle(ABC):
    def __init__(self, *args, **kwargs):
        self._t = Turtle()
        self._direction = 0
        self._half_width = 0
        self._half_height = 0
        self._unit = 0