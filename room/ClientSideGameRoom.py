import time
from threading import Thread

from definitions.TurtlyCommands import TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from room.AbstractGameRoom import AbstractGameRoom
from turtly.Hermes import Hermes


class ClientSideGameRoom(AbstractGameRoom, Thread):
    def __init__(self, *args, **kwargs):
        AbstractGameRoom.__init__(self, *args, **kwargs)
        Thread.__init__(self)
        self._connection = kwargs.get(TurtlyDataKeys.CLIENT_SIDE_GAME_ROOM_TCP_CONNECTION.value, None)

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
                        print("Command not found")
            if wait:
                time.sleep(0.1)

        if not self._closed:
            print("Connection closed - something went wrong or server closed connection")

    def _readyToPlay(self, *args, **kwargs):
        self._players[kwargs.get(TurtlyDataKeys.PLAYER_UUID.value, None)].set_ready()
        print("Set ready to play")

    def _startGame(self, *args, **kwargs):
        self.lock()

    def _identification(self, *args, **kwargs):
        pass

    @property
    def Connection(self):
        return self._connection
