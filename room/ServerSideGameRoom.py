from definitions.TurtlyCommands import TurtlyClientCommands, TurtlyCommandsType, TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from room.AbstractGameRoom import AbstractGameRoom
from turtly.Hermes import Hermes


class ServerSideGameRoom(AbstractGameRoom):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

    def _send_to_all_players(self, command, type, **kwargs):
        for player in self._players.values():
            player.Connection.send(
                Hermes(command,
                       type,
                       **kwargs
                       ))

    def _readyToPlay(self, *args, **kwargs):
        print("Set player ready to play", args, kwargs)
        self._players[kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_ready()
        self._send_to_all_players(TurtlyGameRoomCommands.READY_TO_PLAY,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _startGame(self, *args, **kwargs):
        self.lock()

    def _identification(self, *args, **kwargs):
        pass
