import threading
from time import sleep

from definitions.TurtlyCommands import TurtlyClientCommands, TurtlyCommandsType, TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from room.AbstractGameRoom import AbstractGameRoom
from turtly.Hermes import Hermes


class ServerSideGameRoom(AbstractGameRoom):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _game_loop(self):
        print("-> Serverside game loop")
        while self._started:
            for player in self._players.values():
                self._move_forward(**{TurtlyDataKeys.PLAYER_UUID.value: player.UUID})
            sleep(1)

    def _init_game(self):
        for player in self._players.values():
            player.initialize_turtle(**{TurtlyDataKeys.PLAYER_UUID.value: player.UUID})


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
        print("-> Set player ready to play", args, kwargs)
        self._players[kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_ready()
        self._send_to_all_players(TurtlyGameRoomCommands.READY_TO_PLAY,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _startGame(self, *args, **kwargs):
        print("-> Start game", args, kwargs)
        self.lock()

        print("-> Initialize game", args, kwargs)
        self._init_game()

        print("-> Room locked", args, kwargs)
        self.started()
        print("-> Room started", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.START_GAME,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)
        print("-> Start game loop")
        threading.Thread(target=self._game_loop).start()

    def _identification(self, *args, **kwargs):
        pass

    def _sync(self, *args, **kwargs):
        print("-> Synced", args, kwargs)
        player_representations = {}
        for key, player in self._players.items():
            player_representations[key] = player.Representation
        new_kwargs = {TurtlyDataKeys.GAME_ROOM_UUID.value: self.UUID,
                      TurtlyDataKeys.GAME_ROOM_NAME.value: self.Name,
                      TurtlyDataKeys.GAME_ROOM_PLAYERS_REPRESENTATION.value: player_representations,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: self._adminPlayer.Name,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: self._adminPlayer.UUID,
                      TurtlyDataKeys.GAME_ROOM_LOCKED.value: self._locked,
                      TurtlyDataKeys.GAME_ROOM_CLOSED.value: self._closed,
                      TurtlyDataKeys.GAME_ROOM_STARTED.value: self._started}

        self._send_to_all_players(TurtlyGameRoomCommands.SYNC,
                                  TurtlyCommandsType.RESPONSE,
                                  **new_kwargs)

    def _turn_left(self, *args, **kwargs):
        print("-> Turn left", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.TURN_LEFT,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _turn_right(self, *args, **kwargs):
        print("-> Turn right", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.TURN_RIGHT,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _move_forward(self, *args, **kwargs):
        print("-> Move forward", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.MOVE_FORWARD,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _pause(self, *args, **kwargs):
        print("-> Pause", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.PAUSE,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _escape(self, *args, **kwargs):
        print("-> Escape", args, kwargs)
        self._send_to_all_players(TurtlyGameRoomCommands.ESCAPE,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)
