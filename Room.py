from threading import Thread

from Player import Player
from equipments.security.Unique import Unique


class Room(Unique, Thread):
    def __init__(self, *args, **kwargs):
        Unique.__init__(self)
        Thread.__init__(self)
        self.generate_uuid()
        self._name: str = kwargs.get("name", "Anonymous")
        self._players: list[Player] = []
        self.bindPlayer(kwargs.get("creatorTurtle", None))
        self._creatorPlayer: Player = kwargs.get("creatorTurtle", None)
        self._lock = False

    def bindPlayer(self, player):
        if self._lock:
            print("Room is locked!")
            return
        self._players.append(player)
        player.set_room(self)

    def lock(self):
        self._lock = True

    @property
    def getName(self) -> str:
        return self._name

    @property
    def getPlayerNames(self):
        return [player.get_name() for player in self._players]

    @property
    def getCreatorPlayerName(self):
        return self._creatorPlayer.get_name()

    @property
    def getSelectionDict(self):
        data = {"room_name": self.getName, "creator_name": self.getCreatorPlayerName, "players": self.getPlayerNames}
        return data
