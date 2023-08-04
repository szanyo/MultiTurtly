import time
from threading import Thread

from definitions.TurtlyDataKeys import TurtlyDataKeys
from netturtle.ServerSideNetTurtle import ServerSideNetTurtle
from player.AbstractPlayer import AbstractPlayer
from room.ServerSideGameRoom import ServerSideGameRoom
from turtly.Hermes import Hermes, HermesInterpreter


class ServerSidePlayer(AbstractPlayer, ServerSideNetTurtle, Thread):
    def __init__(self, *args, **kwargs):
        AbstractPlayer.__init__(self, *args, **kwargs)
        ServerSideNetTurtle.__init__(self, *args, **kwargs)
        Thread.__init__(self)
        self._connection = kwargs.get(TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value, None)
        self._binded = False
        self._destroyed = False

    def set_room(self, room):
        self._binded = False
        super().set_room(room)
        if isinstance(room, ServerSideGameRoom):
            self._binded = True

    def run(self):
        while not self._destroyed:
            while self._binded and not self._room.Closed:
                wait = True
                if not self._connection.Queue.empty():
                    msg = self._connection.Queue.get()
                    if isinstance(msg, Hermes):
                        # server received a Hermes message, that controls the game from server side
                        if self._room.HermesInterpreter.execute_command(msg):
                            wait = False
                        else:
                            print("Command not found")
                if wait:
                    time.sleep(0.1)
            time.sleep(0.1)

        print("server closed - exiting now ... (something went wrong or server closed)")

    @property
    def Connection(self):
        return self._connection

    @property
    def Representation(self):
        representation = {TurtlyDataKeys.PLAYER_UUID.value: self.UUID,
                          TurtlyDataKeys.PLAYER_NAME.value: self.Name,
                          TurtlyDataKeys.PLAYER_READY.value: self._isReady}
        return representation
