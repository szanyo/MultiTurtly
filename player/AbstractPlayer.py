from abc import ABC

from bpe.equipments.security.Unique import Unique
from definitions.TurtlyDataKeys import TurtlyDataKeys


class AbstractPlayer(Unique, ABC):
    _instance_num = 0

    def __init__(self, *args, **kwargs):
        Unique.__init__(self, kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None))
        ABC.__init__(self)
        self.generate_uuid()
        self._player_name = kwargs.get(TurtlyDataKeys.PLAYER_NAME.value, "Anonymous_" + str(AbstractPlayer._instance_num))
        self._room = None
        self._isReady = False

    def set_room(self, room):
        self._room = room

    def set_ready(self):
        self._isReady = True

    @property
    def Room(self):
        return self._room

    @property
    def Name(self):
        return self._player_name

    @property
    def Ready(self):
        return self._isReady

    @property
    def Connection(self):
        return None
