import base64
import os
import sys
import time
from threading import Thread

from turtly.Hermes import Hermes, HermesInterpreter
from player.AbstractPlayer import AbstractPlayer
from player.ServerSidePlayer import ServerSidePlayer
from room.ServerSideGameRoom import ServerSideGameRoom
from definitions.TurtlyCommands import TurtlyServerCommands, TurtlyClientCommands, TurtlyCommandsType
from definitions.TurtlyDataKeys import TurtlyDataKeys
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


class TurtlyServer(Thread):
    def __init__(self):
        super().__init__()
        self._tcp_server = MultiClientServer(**init_config())
        self._tcp_server.start()
        self._rooms = {}
        self._players = {}
        self._hermes_interpreter = HermesInterpreter()
        self._exit = False

        self._initHermesCommands()

    def _initHermesCommands(self):
        self._hermes_interpreter.register_command(
            TurtlyServerCommands.NEW_PLAYER_REGISTRATION,
            self._new_player_registration)
        self._hermes_interpreter.register_command(
            TurtlyServerCommands.OPEN_NEW_GAME_ROOM,
            self._open_new_game_room)
        self._hermes_interpreter.register_command(
            TurtlyServerCommands.JOIN_TO_GAME_ROOM,
            self._join_to_game_room)
        self._hermes_interpreter.register_command(
            TurtlyServerCommands.LIST_GAME_ROOMS,
            self._list_game_rooms)

    def _new_player_registration(self, *args, **kwargs):
        print("New player registration", args, kwargs)
        new_player = ServerSidePlayer(*args, **kwargs)
        new_player.start()
        self._players[new_player.UUID] = new_player
        client_connection = kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value]
        client_connection.send(
            Hermes(TurtlyClientCommands.NEW_PLAYER_REGISTRATION,
                   TurtlyCommandsType.RESPONSE,
                   **{TurtlyDataKeys.PLAYER_UUID.value: new_player.UUID,
                      TurtlyDataKeys.PLAYER_NAME.value: new_player.Name}
                   ))

    def _open_new_game_room(self, *args, **kwargs):
        print("Opening new game room", args, kwargs)
        admin_player = self._players[kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value]]
        kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = admin_player
        new_room = ServerSideGameRoom(*args, **kwargs)
        self._rooms[new_room.UUID] = new_room
        new_room.bindPlayer(admin_player)
        self._players.pop(kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value])
        self._tcp_server.client_connections.remove(kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value])

        kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value].send(
            Hermes(TurtlyClientCommands.OPEN_NEW_GAME_ROOM,
                   TurtlyCommandsType.RESPONSE,
                   **{TurtlyDataKeys.GAME_ROOM_UUID.value: new_room.UUID,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: new_room.AdminPlayer.UUID,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: new_room.AdminPlayer.Name,
                      TurtlyDataKeys.GAME_ROOM_NAME.value: new_room.Name}
                   ))

    def _join_to_game_room(self, *args, **kwargs):
        print("Joining to game room", args, kwargs)
        game_room = self._rooms[kwargs[TurtlyDataKeys.GAME_ROOM_UUID.value]]
        player = self._players[kwargs[TurtlyDataKeys.PLAYER_UUID.value]]
        game_room.bindPlayer(player)
        self._players.pop(kwargs[TurtlyDataKeys.PLAYER_UUID.value])
        self._tcp_server.client_connections.remove(kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value])

        kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value].send(
            Hermes(TurtlyClientCommands.JOIN_TO_GAME_ROOM,
                   TurtlyCommandsType.RESPONSE,
                   **{TurtlyDataKeys.GAME_ROOM_UUID.value: game_room.UUID,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: game_room.AdminPlayer.UUID,
                      TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: game_room.AdminPlayer.Name,
                      TurtlyDataKeys.GAME_ROOM_NAME.value: game_room.Name}
                   ))

    def _list_game_rooms(self, *args, **kwargs):
        print("Listing game rooms", args, kwargs)
        game_room_list = [{TurtlyDataKeys.GAME_ROOM_UUID.value: room.UUID,
                           TurtlyDataKeys.GAME_ROOM_NAME.value: room.Name,
                           TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value: room.AdminPlayer.Name,
                           TurtlyDataKeys.GAME_ROOM_PLAYERS_NAMES.value: [player.Name for player in room.Players.values()]}
                          for room in self._rooms.values()]
        client_connection = kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value]
        client_connection.send(
            Hermes(TurtlyClientCommands.LIST_GAME_ROOMS,
                   TurtlyCommandsType.RESPONSE,
                   **{TurtlyDataKeys.GAME_ROOMS.value: game_room_list}
                   ))

    def run(self):
        self.loop()

    def loop(self):
        while True:
            wait = True
            if self._tcp_server.is_closed():
                break
            for client in self._tcp_server.client_connections:
                if not client.Queue.empty():
                    msg = client.Queue.get()
                    if isinstance(msg, Hermes):
                        msg.kwargs[TurtlyDataKeys.SERVER_SIDE_PLAYER_TCP_CONNECTION.value] = client
                        # server received a Hermes message, that controls the game from server side
                        if self._hermes_interpreter.execute_command(msg):
                            wait = False
                        else:
                            print("Command not found")
            if wait:
                time.sleep(0.1)

        print("server closed - exiting now ... (something went wrong or server closed)")
