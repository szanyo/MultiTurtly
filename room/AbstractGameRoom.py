from abc import ABC, abstractmethod

from definitions.TurtlyCommands import TurtlyGameRoomCommands
from player.AbstractPlayer import AbstractPlayer
from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.security.Unique import Unique
from turtly.Hermes import HermesInterpreter


def roomNameValidator(room_name: str):
    """
    Validates the room name
    :param room_name: The new room name to validate
    :return: True if the room name is valid, False otherwise
    """
    return room_name != "" and room_name is not None and len(room_name) > 3


class AbstractGameRoom(Unique, ABC):
    def __init__(self, *args, **kwargs):
        room_uuid = kwargs.get(TurtlyDataKeys.GAME_ROOM_UUID.value, None)
        room_name = kwargs.get(TurtlyDataKeys.GAME_ROOM_NAME.value, "Anonymous")
        game_room_admin = kwargs.get(TurtlyDataKeys.GAME_ROOM_ADMIN.value, AbstractPlayer())

        Unique.__init__(self, room_uuid)
        ABC.__init__(self)

        self.generate_uuid()

        self._locked = False
        self._closed = False
        self._started = False

        self._room_name: str = room_name
        self._players = {}
        self._adminPlayer: AbstractPlayer = game_room_admin

        self._hermes_interpreter = HermesInterpreter()

        self._initHermesCommands()

    def _initHermesCommands(self):
        self._hermes_interpreter.register_command(TurtlyGameRoomCommands.READY_TO_PLAY, self._readyToPlay)
        self._hermes_interpreter.register_command(TurtlyGameRoomCommands.START_GAME, self._startGame)
        self._hermes_interpreter.register_command(TurtlyGameRoomCommands.IDENTIFICATION, self._identification)
        self._hermes_interpreter.register_command(TurtlyGameRoomCommands.SYNC, self._sync)

    def bindPlayer(self, player):
        if self._locked:
            print("Room is locked!")
            return
        self._players[player.UUID] = player
        player.set_room(self)

    def unbindPlayer(self, player):
        if self._locked:
            print("Room is locked!")
            return
        if player in self._players:
            if player == self._adminPlayer:
                self._replaceAdminPlayer()
            self._players.pop(player.UUID)
        player.set_room(None)

    def _replaceAdminPlayer(self):
        if len(self._players) > 0:
            self._adminPlayer = self._players[0]
        else:
            self._adminPlayer = None

    def lock(self):
        self._locked = True

    def unlock(self):
        self._locked = False

    def started(self):
        self._started = True

    def finished(self):
        self._started = False

    @abstractmethod
    def _readyToPlay(self, *args, **kwargs):
        pass

    @abstractmethod
    def _startGame(self, *args, **kwargs):
        pass

    @abstractmethod
    def _identification(self, *args, **kwargs):
        pass

    @abstractmethod
    def _sync(self, *args, **kwargs):
        pass

    @property
    def Closed(self) -> bool:
        return self._closed

    @property
    def Name(self) -> str:
        return self._room_name

    @property
    def AdminPlayer(self):
        return self._adminPlayer

    @property
    def Players(self):
        return self._players

    @property
    def HermesInterpreter(self):
        return self._hermes_interpreter
