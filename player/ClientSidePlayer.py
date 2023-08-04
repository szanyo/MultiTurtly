from definitions.TurtlyDataKeys import TurtlyDataKeys
from netturtle.ClientSideNetTurtle import ClientSideNetTurtle
from player.AbstractPlayer import AbstractPlayer


class ClientSidePlayer(AbstractPlayer, ClientSideNetTurtle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sync(self, representation):
        if self._uuid != representation.get(TurtlyDataKeys.PLAYER_UUID.value, None):
            print("Player UUID mismatch! Changing UUID!")
            self._uuid = representation.get(TurtlyDataKeys.PLAYER_UUID.value, self._uuid)
        self._player_name = representation.get(TurtlyDataKeys.PLAYER_NAME.value, self._player_name)
        self._isReady = representation.get(TurtlyDataKeys.PLAYER_READY.value, self._isReady)


