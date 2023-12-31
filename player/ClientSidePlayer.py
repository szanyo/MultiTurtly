from definitions.TurtlyDataKeys import TurtlyDataKeys
from netturtle.ClientSideNetTurtle import ClientSideNetTurtle
from player.AbstractPlayer import AbstractPlayer


class ClientSidePlayer(AbstractPlayer, ClientSideNetTurtle):
    def __init__(self, *args, **kwargs):
        AbstractPlayer.__init__(self, *args, **kwargs)
        ClientSideNetTurtle.__init__(self, *args, **kwargs)

    def sync(self, representation):
        if self._uuid != representation.get(TurtlyDataKeys.PLAYER_UUID.value, None):
            print("Player UUID mismatch! Changing UUID!")
            self._uuid = representation.get(TurtlyDataKeys.PLAYER_UUID.value, self._uuid)
        self._player_name = representation.get(TurtlyDataKeys.PLAYER_NAME.value, self._player_name)
        self._isReady = representation.get(TurtlyDataKeys.PLAYER_READY.value, self._isReady)
        self._turtle_color = representation.get(TurtlyDataKeys.PLAYER_COLOR.value, self._turtle_color)
        self._turtle_initial_position = representation.get(TurtlyDataKeys.PLAYER_INITIAL_POSITION.value, self._turtle_initial_position)
        self._turtle_initial_direction = representation.get(TurtlyDataKeys.PLAYER_INITIAL_DIRECTION.value, self._turtle_initial_direction)


