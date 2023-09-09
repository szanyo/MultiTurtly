import asyncio
import base64
import os
import sys
import time
from threading import Thread

from bpe.equipments.networking import Networking
from bpe.equipments.networking.Networking import CLIENT_CONFIG_FILE_LOCATION, JSONNetworkConfig, NetworkingEvents
from bpe.equipments.networking.TCP.ClientTCP import Client
from bpe.equipments.security.Cryptography import Cryptography, generate_custom_key

from definitions.TurtlyCommands import TurtlyServerCommands, TurtlyClientCommands, TurtlyGameRoomCommands
from definitions.TurtlyDataKeys import TurtlyDataKeys
from graphics.Graphics import Graphics, GraphicsCommands
from player.ClientSidePlayer import ClientSidePlayer
from room.ClientSideGameRoom import ClientSideGameRoom
from turtly.Hermes import HermesInterpreter, Hermes
from turtly.IndentedOutput import IndentedOutput


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
    if kwargs["server_ip"] == "" or int(kwargs["server_port"]) == 0:

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
        self._roomList = []
        self._close = False
        self._focused = True

        self._initHermesCommands()

    def _initHermesCommands(self):
        self._hermes_interpreter.register_command(TurtlyClientCommands.NEW_PLAYER_REGISTRATION, self._registerPlayer)
        self._hermes_interpreter.register_command(TurtlyClientCommands.LIST_GAME_ROOMS, self._updateRoomList)
        self._hermes_interpreter.register_command(TurtlyClientCommands.OPEN_NEW_GAME_ROOM, self._createRoom)
        self._hermes_interpreter.register_command(TurtlyClientCommands.JOIN_TO_GAME_ROOM, self._joinRoom)

    def registerPlayer(self, name):
        print("-> Registering player")
        kwargs = {TurtlyDataKeys.PLAYER_NAME.value: name}
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.NEW_PLAYER_REGISTRATION, **kwargs))
        asyncio.run(self.until_new_player_registered())  # Wait until player is registered on server side
        print("-> Player registration complete")

    def _registerPlayer(self, **kwargs):
        self._player = ClientSidePlayer(**kwargs)
        print("-> Player registered")

    def updateRoomList(self):
        print("-> Updating room list")
        self._roomListUpToDate = False
        self._roomList = []
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.LIST_GAME_ROOMS))
        asyncio.run(self.until_room_list_updated())  # Wait until room list is updated on server side
        print("-> Room list update complete")

    def _updateRoomList(self, **kwargs):
        print("-> Room list updated")
        self._roomListUpToDate = True
        self._roomList = kwargs[TurtlyDataKeys.GAME_ROOMS.value]
        i = 0
        for room in kwargs[TurtlyDataKeys.GAME_ROOMS.value]:
            i += 1
            prefix = "-" * 3
            postfix = "-" * 100
            print(f"{prefix}Room {i}{postfix}")
            with IndentedOutput():
                IndentedOutput.print(f"Room name:\t\t{room[TurtlyDataKeys.GAME_ROOM_NAME.value]}")
                IndentedOutput.print(f"Room unique id:\t{room[TurtlyDataKeys.GAME_ROOM_UUID.value]}")
                IndentedOutput.print(f"Room admin:\t\t{room[TurtlyDataKeys.GAME_ROOM_ADMIN_NAME.value]}")
                IndentedOutput.print("Players of room:")
                with IndentedOutput():
                    for player in room[TurtlyDataKeys.GAME_ROOM_PLAYERS_NAMES.value]:
                        IndentedOutput.print(f"{player}")

    def createRoom(self, name):
        print("-> Creating room")

        for room in self._roomList:
            if room[TurtlyDataKeys.GAME_ROOM_NAME.value] == name:
                print("-> Room with this name already exists")
                return False

        kwargs = {TurtlyDataKeys.GAME_ROOM_NAME.value: name,
                  TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value: self._player.UUID}
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.OPEN_NEW_GAME_ROOM, **kwargs))
        asyncio.run(self.until_player_joined_to_room())  # Wait until room is created on server side
        print("-> Room creation complete")
        return True

    def _createRoom(self, **kwargs):
        if self._player.UUID == kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN_UUID.value]:
            kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = self._player
        else:
            # This would never be executed, because server would not send this command to other players
            kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = ClientSidePlayer(**kwargs)
        kwargs[TurtlyDataKeys.CLIENT_SIDE_GAME_ROOM_TCP_CONNECTION.value] = self._tcp_client

        self._room = ClientSideGameRoom(**kwargs)
        self._room.bindPlayer(kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value])
        self._room.start()
        self._focused = False
        print("-> Room created")

    def joinRoom(self, name):
        # TODO: Check if room locked or closed
        print("-> Joining room")

        room_uuid = None
        for room in self._roomList:
            if room[TurtlyDataKeys.GAME_ROOM_NAME.value] == name:
                room_uuid = room[TurtlyDataKeys.GAME_ROOM_UUID.value]
                break
        if room_uuid is None:
            print("Room not found")
            print("Something went wrong")
            return False

        kwargs = {TurtlyDataKeys.GAME_ROOM_UUID.value: room_uuid,
                  TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}
        self._tcp_client.send(
            Hermes(TurtlyServerCommands.JOIN_TO_GAME_ROOM, **kwargs))
        asyncio.run(self.until_player_joined_to_room())  # Wait until room is joined on server side
        print("-> Room joining complete")
        return True

    def _joinRoom(self, **kwargs):
        kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value] = ClientSidePlayer(**kwargs)
        kwargs[TurtlyDataKeys.CLIENT_SIDE_GAME_ROOM_TCP_CONNECTION.value] = self._tcp_client
        self._room = ClientSideGameRoom(**kwargs)
        self._room.bindPlayer(kwargs[TurtlyDataKeys.GAME_ROOM_ADMIN.value])
        self._room.bindPlayer(self._player)
        self._room.start()
        self._focused = False
        print("-> Joined to room")

    # Only game room commands

    def readyToPlay(self):
        print("-> Ready to play")
        self.sync()
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.READY_TO_PLAY,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))
        asyncio.run(self.until_ready_to_play())  # Wait until player is ready to play on server side
        print("-> Ready to play complete")

    def sync(self):
        print("-> Syncing game room")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.SYNC,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))
        asyncio.run(self.until_sync())  # Wait until player is synced everything on client side and server side
        print("-> Sync complete")

    def startGame(self):
        print("-> Starting the game by admin")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.START_GAME,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))
        self.sync()
        print("-> Game started")

    # Game methods

    def start_listening_graphic_events(self):
        print("-> Start listening graphic events")
        oc = Graphics().ObserverCollection
        oc.get(GraphicsCommands.LEFT).subscribe(self._left)
        oc.get(GraphicsCommands.RIGHT).subscribe(self._right)
        oc.get(GraphicsCommands.FORWARD).subscribe(self._forward)
        oc.get(GraphicsCommands.ESCAPE).subscribe(self._escape)
        oc.get(GraphicsCommands.PAUSE).subscribe(self._pause)
        oc.get(GraphicsCommands.UPDATE_ALL).subscribe(self._update_all_graphics)

    def stop_listening_graphic_events(self):
        print("-> Stop listening graphic events")
        oc = Graphics().ObserverCollection
        oc.get(GraphicsCommands.LEFT).unsubscribe(self._left)
        oc.get(GraphicsCommands.RIGHT).unsubscribe(self._right)
        oc.get(GraphicsCommands.FORWARD).unsubscribe(self._forward)
        oc.get(GraphicsCommands.ESCAPE).unsubscribe(self._escape)
        oc.get(GraphicsCommands.PAUSE).unsubscribe(self._pause)
        oc.get(GraphicsCommands.UPDATE_ALL).unsubscribe(self._update_all_graphics)

    def _left(self):
        print("-> Left")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.TURN_LEFT,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def _right(self):
        print("-> Right")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.TURN_RIGHT,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def _forward(self):
        print("-> Forward")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.MOVE_FORWARD,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def _escape(self):
        print("-> Escape")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.ESCAPE,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def _pause(self):
        print("-> Pause")
        self._tcp_client.send(
            Hermes(TurtlyGameRoomCommands.PAUSE,
                   **{TurtlyDataKeys.PLAYER_UUID.value: self._player.UUID}))

    def _update_all_graphics(self):
        print("-> Update all")
        self._room.redraw()

    # Program methods

    def close(self):
        self._close = True
        self._tcp_client.close()

    def run(self):
        self.loop()

    def loop(self):
        while not self._close:
            if self._focused:
                wait = True
                if self._tcp_client.is_closed():
                    break
                if not self._tcp_client.Queue.empty():
                    msg = self._tcp_client.Queue.get()
                    if isinstance(msg, Hermes):
                        # server received a Hermes message, that controls the game from server side
                        if self._hermes_interpreter.execute_command(msg):
                            wait = False
                        else:
                            print("Command not found in TurtlyClient")
                if wait:
                    time.sleep(0.1)
            else:
                asyncio.run(self.until_room_focused())

        if not self._close:
            print("Connection closed - something went wrong or server closed connection")

    async def until_connection_has_become_alive(self):
        while not self._tcp_client.is_connected():
            await asyncio.sleep(0.1)

    async def until_new_player_registered(self):
        while self._player is None:
            await asyncio.sleep(0.1)

    async def until_room_list_updated(self):
        while not self._roomListUpToDate:
            await asyncio.sleep(0.1)

    async def until_player_joined_to_room(self):
        if self._player is not None:
            while self._player.Room is None:
                await asyncio.sleep(0.1)
        else:
            print("Player not registered yet")
            print("Something went wrong ...")

    async def until_ready_to_play(self):
        while not self._player.Ready:
            await asyncio.sleep(0.1)

    async def until_sync(self):
        while not self._player.Room.Synced:
            await asyncio.sleep(0.1)

    async def until_room_focused(self):
        while self._room is not None:
            await asyncio.sleep(0.1)
        self._focused = True

    def isAdmin(self):
        return self._player.UUID == self._player.Room.AdminPlayer.UUID

    @property
    def Room(self):
        return self._room
