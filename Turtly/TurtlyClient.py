import asyncio
import base64
import os
import sys
import time
from threading import Thread

from Turtly.Hermes import HermesInterpreter, Hermes
from player.AbstractPlayer import AbstractPlayer
from player.ClientSidePlayer import ClientSidePlayer
from room.ServerSideGameRoom import ServerSideGameRoom
from definitions.TurtlyCommands import TurtlyServerCommands, TurtlyClientCommands, TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from equipments.networking import Networking
from equipments.networking.Networking import CLIENT_CONFIG_FILE_LOCATION, JSONNetworkConfig, NetworkingEvents
from equipments.networking.TCP.ClientTCP import Client
from equipments.security.Cryptography import Cryptography, generate_custom_key


def connected(*args, **kwargs):
    print("Connected")


def disconnected(*args, **kwargs):
    print("Disconnected")


def path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    elif __file__:
        return os.path.dirname(__file__)
    else:
        print("WARNING: No path found")
        return os.getcwd()


def init_config():
    file_path = os.path.join(path(), CLIENT_CONFIG_FILE_LOCATION)
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

    Networking.SHW = kwargs["log"]

    return kwargs


class TurtlyClient(Thread):
    def __init__(self):
        super().__init__()
        self._tcp_client = Client(**init_config())
        self._tcp_client.event_handlers.get(NetworkingEvents.CONNECTED).subscribe(connected)
        self._tcp_client.event_handlers.get(NetworkingEvents.DISCONNECTED).subscribe(disconnected)
        self._tcp_client.connect()
        self._tcp_client.start()
        self._hermes_interpreter = HermesInterpreter()
        self._player = None
        self._room = None
        self._roomListUpToDate = False
        self._close = False

        self._initHermesCommands()

    def _initHermesCommands(self):
        self._hermes_interpreter.register_command(TurtlyClientCommands.NEW_PLAYER_REGISTRATION, self._registerPlayer)
        self._hermes_interpreter.register_command(TurtlyClientCommands.LIST_GAME_ROOMS, self._updateRoomList)
        self._hermes_interpreter.register_command(TurtlyClientCommands.OPEN_NEW_GAME_ROOM, self._createRoom)

    def registerPlayer(self, name):
        print("Registering player")
        kwargs = {TurtlyDataKeys.PLAYER_NAME.value: name}
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.NEW_PLAYER_REGISTRATION, **kwargs))
        asyncio.run(self.until_new_player_registered())  # Wait until player is registered on server side
        print("Player registration complete")

    def _registerPlayer(self, **kwargs):
        kwargs[TurtlyDataKeys.PLAYER_TCP_CLIENT_CONNECTION.value] = self._tcp_client
        self._player = ClientSidePlayer(**kwargs)
        print("Player registered")

    def updateRoomList(self):
        print("Updating room list")
        self._roomListUpToDate = False
        self._tcp_client.send(
            Hermes(TurtlyClientCommands.LIST_GAME_ROOMS))
        asyncio.run(self.until_room_list_updated())  # Wait until room list is updated on server side
        print("Room list update complete")

    def _updateRoomList(self, **kwargs):
        print("Room list updated")
        self._roomListUpToDate = True

    def createRoom(self, name):
        print("Creating room")
        kwargs = {TurtlyDataKeys.GAME_ROOM_NAME.value: name,
                  TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: self._player.UUID}
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.OPEN_NEW_GAME_ROOM, **kwargs))
        asyncio.run(self.until_room_created())  # Wait until room is created on server side
        print("Room creation complete")

    def _createRoom(self, **kwargs):
        if self._player.UUID == kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value]:
            kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = self._player
        else:
            # TODO: the else part is not needed, the server should send the player info
            player_kwargs = {TurtlyDataKeys.PLAYER_UUID.value: kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value],
                             TurtlyDataKeys.PLAYER_NAME.value: kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value]}
            kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = AbstractPlayer(**player_kwargs)
        self._room = ServerSideGameRoom(**kwargs)
        print("Room created")

    def joinRoom(self, name):
        pass

    def _joinRoom(self, **kwargs):
        pass

    def readyToPlay(self):
        print("Ready to play")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.READY_TO_PLAY,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def updateInfo(self):
        pass

    def close(self):
        self._close = True
        self._tcp_client.close()

    def run(self):
        self.loop()

    def loop(self):
        while not self._close:
            wait = True
            if self._tcp_client.is_closed():
                break
            if not self._tcp_client.get_queue().empty():
                msg = self._tcp_client.get_queue().get()
                if isinstance(msg, Hermes):
                    # server received a Hermes message, that controls the game from server side
                    if self._hermes_interpreter.execute_command(msg):
                        wait = False
                    else:
                        print("Command not found")
            if wait:
                time.sleep(0.1)

        if not self._close:
            print("Connection closed - something went wrong or server closed connection")

    async def until_connection_has_become_alive(self):
        while not self._tcp_client.is_connected():
            await asyncio.sleep(0.5)

    async def until_new_player_registered(self):
        while self._player is None:
            await asyncio.sleep(0.5)

    async def until_room_list_updated(self):
        while not self._roomListUpToDate:
            await asyncio.sleep(0.5)

    async def until_room_created(self):
        if self._player is not None:
            while self._player.get_room() is None:
                await asyncio.sleep(0.5)
        else:
            print("Player not registered yet")
            print("Something went wrong ...")
