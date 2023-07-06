from NetTurtle import NetTurtle
from equipments.security.Unique import Unique


class Player(Unique):
    def __init__(self, *args, **kwargs):
        super().__init__()
        Player._instance_num += 1
        self._name = kwargs.get("name", "Anonymous_" + str(Player._instance_num))
        self._room = None
        self._netTurtle = None
        self._tcp_client = kwargs.get("client_connection", None)
        self._isReady = False

    def set_room(self, room):
        self._room = room

    def get_room(self):
        return self._room

    def get_name(self):
        return self._name
