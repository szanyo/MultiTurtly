#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.10 "
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"

import pickle
from enum import Enum, auto

from equipments.io.JSONContainer import JSONContainer

SERVER_CONFIG_FILE_LOCATION = "server.json"

CLIENT_CONFIG_FILE_LOCATION = "client.json"

SHW = True


def inform(show, *args, **kwargs):
    if show:
        print(*args, **kwargs)


class NetworkingEvents(Enum):
    """Constants for the network events"""
    CONNECTED = auto()
    # In most cases, this is one of the events that would be used outside the networking module

    DISCONNECTED = auto()
    # In most cases, this is one of the events that would be used outside the networking module

    CREATED = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used

    ABORTED = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used

    CLOSED = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used

    REFUSED = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used

    RESET = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used

    WAITING_FOR_NEW_CONNECTION = auto()
    # Unnecessary to use outside the networking module (internal use), but can be used


def is_pickle_stream(stream):
    """
    Pickle stream checker

    :param stream: Byte stream that is going to be checked if it is a pickle stream
    :return: True if the stream is a pickle stream, False if it is not
    """
    try:
        pickle.loads(stream)
        return True
    except pickle.UnpicklingError:
        return False
    except Exception:
        return False


class TransferMode(Enum):
    """
    Mode of the connection

    SIMPLE: Consumes only 1024 bytes of data in one message
    COMPLEX: Consumes unlimited size of data in one message
    """
    SIMPLE = 0
    COMPLEX = 1


class ControlCommands(Enum):
    """
    Internal commands for the networking

    These commands are going to be sent to the other side of the connection, and the other side will react to them
    """
    CHECK_CONNECTION = auto()
    CONNECTION_IS_ALIVE = auto()
    CONNECTION_IS_NOT_ALIVE = auto()
    CRYPTOGRAPHY_INVALID = auto()
    ACKNOWLEDGE = auto()
    CLOSE = auto()


class JSONNetworkConfig(JSONContainer):
    def __init__(self, file_location):
        super().__init__()
        self._ip = ""
        self._port = 0
        self._salt = bytes()
        self._password = ""
        self._log = True
        self._file_location = file_location
        self._load()

    def fromDict(self, dict):
        self._ip = dict.get("server_ip", self._ip)
        self._port = dict.get("server_port", self._port)
        self._salt = dict.get("salt", self._salt)
        self._password = dict.get("password", self._password)
        self._log = dict.get("log", self._log)

    def toDict(self):
        return {"server_ip": self._ip,
                "server_port": self._port,
                "salt": self._salt,
                "password": self._password,
                "log": self._log}
