import base64
import os
import sys
import time

from Hermes import HermesInterpreter, Hermes
from TurtlyServerCommands import TurtlyServerCommands
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


class TurtlyClient:
    def __init__(self):
        self._tcp_client = Client(**init_config())
        self._tcp_client.event_handlers.get(NetworkingEvents.CONNECTED).subscribe(connected)
        self._tcp_client.event_handlers.get(NetworkingEvents.DISCONNECTED).subscribe(disconnected)
        self._tcp_client.connect()
        self._tcp_client.start()
        self._hermes_interpreter = HermesInterpreter()
        self._exit = False

        self._initHermesCommands()
        self.loop()

    def _initHermesCommands(self):
        pass

    def loop(self):
        while True:
            wait = True
            if self._tcp_client.is_closed():
                break
            if not self._tcp_client.get_queue().empty():
                msg = self._tcp_client.get_queue().get()
                if isinstance(msg, Hermes):
                    # Server received a Hermes message, that controls the game from server side
                    if self._hermes_interpreter.execute_command(msg):
                        wait = False
                    else:
                        print("Command not found")
            if wait:
                time.sleep(0.1)

        print("Connection closed - something went wrong or server closed connection")
