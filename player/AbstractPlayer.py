from abc import ABC

from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.security.Unique import Unique
from room.AbstractRoom import AbstractRoom


class AbstractPlayer(Unique, ABC):
    _instance_num = 0

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None))
        self.generate_uuid()
        self._name = kwargs.get(TurtlyDataKeys.PLAYER_NAME.value, "Anonymous_" + str(AbstractPlayer._instance_num))
        self._room = None
        self._netTurtle = None
        self._isReady = False

    def set_room(self, room):
        self._room = room

    def get_room(self):
        return self._room

    @property
    def Name(self):
        return self._name
