import threading
from time import sleep, time

from definitions import TurtlyPredefinedDirections
from definitions.TurtlyCommands import TurtlyClientCommands, TurtlyCommandsType, TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from definitions.TurtlyPredefinedPositions import TurtlyPredefinedPositions
from equipments.multitools.Bicska import generate_distinct_colors
from room.AbstractGameRoom import AbstractGameRoom
from turtly.Hermes import Hermes


class ServerSideGameRoom(AbstractGameRoom):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _game_loop(self):
        print("-> Serverside game loop")
        self._startTime = time() + 3

        print(f"-> Server time: {self._startTime}")
        print(f"-> Starting in 3 seconds")
        while self._startTime < time():
            sleep(0.01)

        print(f"-> {time()}")
        print("-> Let's go!")
        while self._toggles["started"]:
            for player in self._players.values():
                self._move_forward(**{TurtlyDataKeys.PLAYER_UUID.value: player.UUID})
            sleep(1)

    def _init_game(self):
        counter = 0
        prepositions = list(TurtlyPredefinedPositions.items())
        predirections = TurtlyPredefinedDirections.TurtlyPredifinedDirections
        colors = generate_distinct_colors(len(self._players), min_lightness=0.5,max_lightness=1.0, min_saturation=0.5, max_saturation=1.0, color_offset=50)
        for player in self._players.values():
            player._turtle_color = colors[counter]
            player._turtle_initial_position = prepositions[counter][1]
            player._turtle_initial_direction = predirections[counter]
            counter += 1

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

    def _identification(self, *args, **kwargs):
        pass

    def _readyToPlay(self, *args, **kwargs):
        print("-> Set player ready to play", args, kwargs)
        self._players[kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_ready()
        self._send_to_all_players(TurtlyGameRoomCommands.READY_TO_PLAY,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)

    def _startGame(self, *args, **kwargs):
        print("-> Start game", args, kwargs)

        self.lock()
        print("-> Room locked", args, kwargs)

        self._init_game()
        print("-> Game initialized", args, kwargs)

        self.started()
        print("-> Room started", args, kwargs)

        self._send_to_all_players(TurtlyGameRoomCommands.START_GAME,
                                  TurtlyCommandsType.RESPONSE,
                                  **kwargs)
        print("-> Start game loop")
        threading.Thread(target=self._game_loop).start()

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
                      TurtlyDataKeys.GAME_ROOM_LOCKED.value: self._toggles["locked"],
                      TurtlyDataKeys.GAME_ROOM_CLOSED.value: self._toggles["closed"],
                      TurtlyDataKeys.GAME_ROOM_STARTED.value: self._toggles["started"],}

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
