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

    def _send_to_player(self, command, type, player_uuid, **kwargs):
        self._players[player_uuid].Connection.send(
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

    def _sync(self, *args, **kwargs):
        print("Synced", args, kwargs)
        player_representations = {}
        for key, player in self._players.items():
            player_representations[key] = player.Representation
        new_kwargs = {TurtlyDataKeys.GAME_ROOM_UUID.value: self.UUID,
                      TurtlyDataKeys.GAME_ROOM_NAME.value: self.Name,
                      TurtlyDataKeys.GAME_ROOM_PLAYERS_REPRESENTATION.value: player_representations,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: self._adminPlayer.Name,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: self._adminPlayer.UUID,
                      TurtlyDataKeys.GAME_ROOM_LOCKED.value: self._locked,
                      TurtlyDataKeys.GAME_ROOM_CLOSED.value: self._closed}

        self._send_to_all_players(TurtlyGameRoomCommands.SYNC,
                                  TurtlyCommandsType.RESPONSE,
                                  **new_kwargs)
