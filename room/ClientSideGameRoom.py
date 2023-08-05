import time
from enum import Enum, auto
from threading import Thread

import pyconio
from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.patterns.Observing import Observer, ObserverCollection
from player.ClientSidePlayer import ClientSidePlayer
from room.AbstractGameRoom import AbstractGameRoom
from turtly.Hermes import Hermes
from turtly.IndentedOutput import IndentedOutput


class ClientSideGameRoomEvents(Enum):
    UPDATE = auto()


class ClientSideGameRoom(AbstractGameRoom, Thread):

    def __init__(self, *args, **kwargs):
        AbstractGameRoom.__init__(self, *args, **kwargs)
        Thread.__init__(self)
        self._connection = kwargs.get(TurtlyDataKeys.CLIENT_SIDE_GAME_ROOM_TCP_CONNECTION.value, None)
        self._event_handler = ObserverCollection()
        self._synced = False

        self._init_event_handlers()

    def _init_event_handlers(self):
        self._event_handler.add(ClientSideGameRoomEvents.UPDATE)

    def run(self):
        while not self._closed:
            wait = True
            if not self._connection.Queue.empty():
                msg = self._connection.Queue.get()
                if isinstance(msg, Hermes):
                    # server received a Hermes message, that controls the game from server side
                    if self._hermes_interpreter.execute_command(msg):
                        wait = False
                    else:
                        print("Command not found in ClientSideGameRoom")
            if wait:
                time.sleep(0.1)

        if not self._closed:
            print("Connection closed - something went wrong or server closed connection")

    def _readyToPlay(self, *args, **kwargs):
        self._players[kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_ready()
        self._event_handler.fire_all()
        print("Set ready to play")

    def _startGame(self, *args, **kwargs):
        self.lock()

    def _identification(self, *args, **kwargs):
        pass

    def _sync(self, *args, **kwargs):
        if kwargs.get(TurtlyDataKeys.GAME_ROOM_UUID.value, None) == self.UUID:
            if self._room_name != kwargs.get(TurtlyDataKeys.GAME_ROOM_NAME.value, None):
                self._room_name = kwargs.get(TurtlyDataKeys.GAME_ROOM_NAME.value, "!!!Synchronization failure!!!")

            self._sync_players(
                kwargs.get(TurtlyDataKeys.GAME_ROOM_PLAYERS_REPRESENTATION.value, "!!!Synchronization failure!!!"))

            if self._adminPlayer.UUID != kwargs.get(TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value, None) \
                    and self._adminPlayer.Name != kwargs.get(TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value, None):
                self._adminPlayer = self._players[
                    kwargs.get(TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value, "!!!Synchronization failure!!!")]

            self._locked = kwargs.get(TurtlyDataKeys.GAME_ROOM_LOCKED.value, False)
            self._closed = kwargs.get(TurtlyDataKeys.GAME_ROOM_CLOSED.value, False)

            self._synced = True

            self._event_handler.fire_all()
            print("Synced")
        else:
            print("Sync failed")
            print("Invalid game room uuid")

    def _sync_players(self, representations):
        if representations != "!!!Synchronization failure!!!":
            for player_uuid in list(self._players.keys()):
                if player_uuid not in representations.keys():
                    self._players.pop(player_uuid)
                else:
                    self._players[player_uuid].sync(representations[player_uuid])
            for player_representation in representations.values():
                if player_representation.get(TurtlyDataKeys.PLAYER_UUID.value, None) not in self._players.keys():
                    self._players[player_representation.get(TurtlyDataKeys.PLAYER_UUID.value, None)] = ClientSidePlayer(
                        **player_representation)
                    self._players[player_representation.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_room(self)
                    self._players[player_representation.get(TurtlyDataKeys.PLAYER_UUID.value, None)].sync(
                        player_representation)
        else:
            print("Sync failed")
            print("Invalid players representation")

    @property
    def Connection(self):
        return self._connection

    @property
    def Synced(self):
        return self._synced

    @property
    def EventHandler(self):
        return self._event_handler

    def print_status(self):
        print(f"Room name:\t\t{self.Name}")
        print(f"Room unique id:\t{self._uuid}")
        print(f"Room admin:\t\t{self._adminPlayer.Name}")
        print(f"Players of room:")
        with IndentedOutput():
            for uuid, player in self._players.items():
                IndentedOutput.print(f"{player.Name}")
                with IndentedOutput():
                    IndentedOutput.print(f"UUID: \t{player.UUID}")
                    IndentedOutput.print(f"Ready: \t{player.Ready}")
                    IndentedOutput.print("")
                    # IndentedOutput.print(f"(dict_id: \t{uuid})")
