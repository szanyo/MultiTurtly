from random import randint

from netturtle.AbstractNetTurtle import AbstractNetTurtle


class ServerSideNetTurtle(AbstractNetTurtle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._turtle_color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self._turtle_initial_position = randint(0, 2), randint(0, 2)
        self._turtle_initial_direction = 90