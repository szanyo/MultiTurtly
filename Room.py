from threading import Thread

from Player import Player
from equipments.security.Unique import Unique


class Room(Unique, Thread):
    def __init__(self, *args, **kwargs):
        Unique.__init__(self, kwargs.get("room_uuid", None))
        Thread.__init__(self)
        self.generate_uuid()
        self._locked = False
        self._name: str = kwargs.get("room_name", "Anonymous")
        self._players: list[Player] = []
        self.bindPlayer(kwargs.get("creatorPlayer", Player()))
        self._creatorPlayer: Player = kwargs.get("creatorPlayer", None)

    def bindPlayer(self, player):
        if self._locked:
            print("Room is locked!")
            return
        self._players.append(player)
        player.set_room(self)

    def lock(self):
        self._locked = True

    @property
    def getName(self) -> str:
        return self._name

    @property
    def getPlayers(self):
        return [player.get_dict() for player in self._players]

    @property
    def getCreatorPlayerName(self):
        return self._creatorPlayer.get_name()

    @property
    def getDict(self):
        data = {"room_name": self.getName,
                "room_uuid": self.uuid,
                "creator_player_name": self.getCreatorPlayerName,
                "creator_player_uuid": self._creatorPlayer.uuid}
        return data
