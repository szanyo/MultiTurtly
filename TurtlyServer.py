import base64
import os
import sys
import time

from Hermes import Hermes, HermesInterpreter
from Room import Room
from TurtlyServerCommands import TurtlyServerCommands
from equipments.networking.Networking import SERVER_CONFIG_FILE_LOCATION, JSONNetworkConfig
from equipments.networking.TCP.MultiClientServerTCP import MultiClientServer
from equipments.security.Cryptography import Cryptography, generate_custom_key


def path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(__file__)
    else:
        print("WARNING: No path found")
        return os.getcwd()


def init_config():
    file_path = os.path.join(path(), SERVER_CONFIG_FILE_LOCATION)
    json_container = JSONNetworkConfig(file_path)
    kwargs = json_container.toDict()
    if kwargs["server_ip"] == "" or int(kwargs["server_ip"]) == 0:

        print("No config file found")
        print("(Press enter to continue with localhost)")

        ip = str(input("IP: "))
        if ip != "":
            kwargs["server_ip"] = ip
        else:
            kwargs.pop("server_ip")

        print("Press enter to continue with port 5051")

        port = input("Port: ")
        if port != "":
            kwargs["server_port"] = int(port)
        else:
            kwargs.pop("server_port")

    else:
        print("Config file found")

    kwargs["security_crypt"] = Cryptography(
        generate_custom_key(base64.b64decode(kwargs["salt"].encode("utf-8")), kwargs["password"]))

    return kwargs


class TurtlyServer:
    def __init__(self):
        self._tcp_server = MultiClientServer(**init_config())
        self._tcp_server.start()
        self._rooms = []
        self._hermes_interpreter = HermesInterpreter()
        self._exit = False

        self._initHermesCommands()
        self.loop()

    def _initHermesCommands(self):
        self._hermes_interpreter.register_command(TurtlyServerCommands.OPEN_NEW_GAME_ROOM, self._open_new_game_room)
        self._hermes_interpreter.register_command(TurtlyServerCommands.JOIN_TO_GAME_ROOM, self._join_to_game_room)
        self._hermes_interpreter.register_command(TurtlyServerCommands.LIST_GAME_ROOMS, self._list_game_rooms)

    def _list_game_rooms(self, *args, **kwargs):
        print("Listing game rooms")
        game_room_list = [room.getSelectionDict() for room in self._rooms]
        kwargs["client_connection"].send(Hermes(TurtlyServerCommands.LIST_GAME_ROOMS, rooms=game_room_list))

    def _open_new_game_room(self, *args, **kwargs):
        new_room = Room(*args, **kwargs)
        self._rooms.append(new_room)
        self._tcp_server.client_connections.remove(kwargs["client_connection"])
        print("Opening new game room")

    def _join_to_game_room(self, *args, **kwargs):
        print("Joining to game room")

    def loop(self):
        while True:
            wait = True
            if self._tcp_server.is_closed():
                break
            for client in self._tcp_server.client_connections:
                if not client.get_queue().empty():
                    msg = client.get_queue().get()
                    if isinstance(msg, Hermes):
                        msg.kwargs["client_connection"] = client
                        # Server received a Hermes message, that controls the game from server side
                        if self._hermes_interpreter.execute_command(msg):
                            wait = False
                        else:
                            print("Command not found")
            if wait:
                time.sleep(0.1)

        print("Server closed - exiting now ... (something went wrong or server closed)")
