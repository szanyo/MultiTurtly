from abc import ABC
from threading import Thread

from player.AbstractPlayer import AbstractPlayer
from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.security.Unique import Unique


class AbstractRoom(Unique, Thread, ABC):
    def __init__(self, *args, **kwargs):
        room_uuid = kwargs.get(TurtlyDataKeys.GAME_ROOM_UUID.value, None)
        room_name = kwargs.get(TurtlyDataKeys.GAME_ROOM_NAME.value, "Anonymous")
        game_room_admin = kwargs.get(TurtlyDataKeys.GAME_ROOM_ADMIN.value, AbstractPlayer())

        Unique.__init__(self, room_uuid)
        Thread.__init__(self)

        self.generate_uuid()

        self._locked = False

        self._name: str = room_name
        self._players: list[AbstractPlayer] = []
        self.bindPlayer(game_room_admin)
        self._adminPlayer: AbstractPlayer = game_room_admin

    def hall(self):
        pass

    def game(self):
        pass

    def run(self):
        pass

    def bindPlayer(self, player):
        if self._locked:
            print("Room is locked!")
            return
        self._players.append(player)
        player.set_room(self)

    def unbindPlayer(self, player):
        if self._locked:
            print("Room is locked!")
            return
        if player in self._players:
            if player == self._adminPlayer:
                self._replaceAdminPlayer()
            self._players.remove(player)
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

    @property
    def Name(self) -> str:
        return self._name

    @property
    def AdminPlayer(self):
        return self._adminPlayer

    @property
    def getPlayersInfo(self):
        return [{TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: player.Name,
                 TurtlyDataKeys.GAME_ROOM_ADMIN_UUID: player.UUID} for player in self._players]
