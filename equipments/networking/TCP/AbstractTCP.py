#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.18"
__status__ = "Production"
__date__ = "2023.06.08"
__license__ = "MIT"

import pickle
import struct
import time
from abc import abstractmethod, ABC
from queue import Queue
from socket import socket, AF_INET, SOCK_STREAM

from equipments.networking import Networking
from equipments.networking.Networking import TransferMode, ControlCommands, NetworkingEvents, is_pickle_stream, inform
from equipments.patterns.Observing import ObserverCollection, Observer
from equipments.security.Cryptography import Cryptography


class AbstractTCP(ABC):
    @property
    def Queue(self):
        return self._queue

    def __init__(self, **kwargs):
        """
        Constructor of the AbstractPartnerTCP class that is the parent of the client and server classes

        :param server_ip: IP address of the server (default: localhost)
        :param server_port: Port of the server (default: 5051)
        :param mode: Mode of the connection (default: TransferMode.COMPLEX)
        (Complex consumes unlimited size of data in one message)
        :param security_crypt: Cryptography object for encrypting and decrypting the message data (default: Crypt())
        """
        self._socket = socket(AF_INET, SOCK_STREAM)  # the socket object
        self._server_address = (
            str(kwargs.get("server_ip", "localhost")),
            kwargs.get("server_port", 5051))
        self._client_address = (None, None)
        self._mode = kwargs.get("mode", TransferMode.COMPLEX)
        self._security_crypt = kwargs.get("security_crypt", None)
        self._queue = Queue()  # Queue for the messages
        self._connected = False
        self._close = False

        # Control messages
        self._control_command_handlers = ObserverCollection()
        self._init_control_event_handlers()

        # Event handlers
        self.event_handlers = ObserverCollection()
        self._init_event_handlers()

    def _init_control_event_handlers(self):
        """
        Initialize the internal control messages of the client
        """
        for controlCommand in ControlCommands:
            self._control_command_handlers.add(controlCommand, controlCommand.name)

        self._control_command_handlers.get(ControlCommands.CHECK_CONNECTION).subscribe(
            self._control_check_connection)
        self._control_command_handlers.get(ControlCommands.CLOSE).subscribe(
            self._control_close)
        self._control_command_handlers.get(ControlCommands.CONNECTION_IS_ALIVE).subscribe(
            self._control_connection_is_alive)
        self._control_command_handlers.get(ControlCommands.CONNECTION_IS_NOT_ALIVE).subscribe(
            self._control_connection_is_not_alive)
        self._control_command_handlers.get(ControlCommands.ACKNOWLEDGE).subscribe(
            self._control_acknowledge)
        self._control_command_handlers.get(ControlCommands.CRYPTOGRAPHY_INVALID).subscribe(
            self._control_cryptography_invalid)

    def _init_event_handlers(self):
        """
        Initialize the internal events of the client

        (External methods can be subscribed to these events
        by using the event_handlers object get(EVENT_TYPE).subscribe() method)
        """
        for eventType in NetworkingEvents:
            self.event_handlers.add(eventType, eventType.name)

        self.event_handlers.get(NetworkingEvents.CONNECTED).subscribe(
            self._connection_connected)
        self.event_handlers.get(NetworkingEvents.DISCONNECTED).subscribe(
            self._connection_disconnected)
        self.event_handlers.get(NetworkingEvents.CREATED).subscribe(
            self._connection_created)
        self.event_handlers.get(NetworkingEvents.ABORTED).subscribe(
            self._connection_lost)
        self.event_handlers.get(NetworkingEvents.CLOSED).subscribe(
            self._connection_closed)
        self.event_handlers.get(NetworkingEvents.REFUSED).subscribe(
            self._connection_refused)
        self.event_handlers.get(NetworkingEvents.RESET).subscribe(
            self._connection_reset)
        self.event_handlers.get(NetworkingEvents.WAITING_FOR_NEW_CONNECTION).subscribe(
            self._connection_waiting_for_new)

    def send(self, msg):
        """
        Send message to the server (msg must be a serializable object)
        :param msg: Message to send
        """
        self._send_complex(msg)  # if self._mode == TransferMode.COMPLEX else self._send_simple(msg)

    def catch(self):
        """
        Catch message from the server
        :return: True if caught valid message, False if not
        """
        return self._catch_complex()  # if self._mode == TransferMode.COMPLEX else self._catch_simple()

    def is_connected(self):
        """
        Check if the client is connected to the server
        :return: True if connected, False if not
        """
        return self._connected

    def is_closed(self):
        """
        Check if the client is closed
        :return: True if closed, False if not
        """
        return self._close

    def _check_connection(self):
        """Check if the connection is alive"""
        self._control_command_handlers.fire(ControlCommands.CHECK_CONNECTION)

    def _catch_complex(self):
        """
        Catch complex message from the server
        :return: True if caught valid message, False if not
        """
        data = self._catch_complex_msg()
        if data is not None:
            if self._security_crypt is not None and isinstance(self._security_crypt, Cryptography):
                msg = self._security_crypt.decrypt(bytes(data))
            else:
                msg = data
            if is_pickle_stream(msg):
                msg = pickle.loads(msg)
                if isinstance(msg, ControlCommands):
                    self._control_command_handlers.fire(msg, f"Sent by {self.getPartnerIP()}")
                else:
                    self._queue.put(msg)
                return True
            else:
                self._control_command_handlers.fire(ControlCommands.CRYPTOGRAPHY_INVALID, msg)
        return False

    def _catch_complex_msg(self):
        """
        Catch a message from the socket that has more than 1024 bytes of data
        :return: The message
        """
        # Read message length and unpack it into an integer
        raw_msglen = self._catch_complex_full_msg(4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the full message data
        return self._catch_complex_full_msg(msglen)

    # NETWORKING CONTROL COMMANDS

    def _control_check_connection(self, *args, **kwargs):
        """
        Internal method for checking the connection
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONTROL_CHECK_CONNECTION", args)
        self._connected = True
        self.send(ControlCommands.CONNECTION_IS_ALIVE)

    def _control_close(self, *args, **kwargs):
        """
        Internal method for closing the connection
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONTROL_CLOSE", args)
        self._connected = False
        self._close = True
        kwargs = {"partner": self}
        self.event_handlers.fire(NetworkingEvents.DISCONNECTED, **kwargs)

    def _control_connection_is_alive(self, *args, **kwargs):
        """
        Internal method for checking if the connection is alive
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONTROL_CONNECTION_IS_ALIVE", args)
        self.send(ControlCommands.ACKNOWLEDGE)

    @abstractmethod
    def _control_connection_is_not_alive(self, *args, **kwargs):
        """
        Internal method for checking if the connection is not alive
        :param args: error message
        :param kwargs: any other arguments
        """
        pass

    def _control_acknowledge(self, *args, **kwargs):
        """
        Internal method for acknowledging the connection
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONTROL_ACKNOWLEDGE", args)
        if not self._connected:
            self._connected = True
        self.event_handlers.fire(NetworkingEvents.CONNECTED)

    def _control_cryptography_invalid(self, *args, **kwargs):
        """
        Internal method for handling the cryptography invalid event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(True, "The cryptography is invalid, the message will be ignored", *args, **kwargs)
        time.sleep(5)

    # NETWORKING EVENTS

    def _connection_connected(self, *args, **kwargs):
        """
        Internal method for handling the connection connected event
        :param args: error message
        :param kwargs: any other arguments
        """
        pass

    def _connection_disconnected(self, *args, **kwargs):
        """
        Internal method for handling the connection disconnected event
        :param args: error message
        :param kwargs: any other arguments
        """
        pass

    def _connection_created(self, *args, **kwargs):
        """
        Internal method for handling the connection created event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_CREATED", args)
        if Networking.SHW:
            self.who_am_i()
            self.who_is_my_new_friend()

    def _connection_lost(self, *args, **kwargs):
        """
        Internal method for handling the connection lost event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_LOST", args)
        self._check_connection()

    def _connection_closed(self, *args, **kwargs):
        """
        Internal method for handling the connection closed event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_CLOSED", args)

    def _connection_refused(self, *args, **kwargs):
        """
        Internal method for handling the connection refused event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_REFUSED", args)
        self._control_command_handlers.fire(ControlCommands.CONNECTION_IS_NOT_ALIVE)

    def _connection_reset(self, *args, **kwargs):
        """
        Internal method for handling the connection reset event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_RESET", args)
        self._check_connection()

    def _connection_aborted(self, *args, **kwargs):
        """
        Internal method for handling the connection aborted event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_ABORTED", args)
        self._check_connection()

    def _connection_waiting_for_new(self, *args, **kwargs):
        """
        Internal method for handling the waiting for new connection event
        """
        inform(Networking.SHW, "CONNECTION_WAITING_FOR_NEW", args)

    @abstractmethod
    def _send_complex(self, msg):
        """
        Send message to the client in complex mode
        :param msg: Message to send
        """
        pass

    # @abstractmethod
    # def _send_simple(self, msg):
    #     """
    #     Catch message from the client in simple mode
    #     :return: True if caught valid message, False if not
    #     """
    #     pass
    #
    # @abstractmethod
    # def _catch_simple(self):
    #     """
    #     Catch message from the client in simple mode
    #     :return: True if caught valid message, False if not
    #     """
    #     pass

    @abstractmethod
    def _catch_complex_full_msg(self, n):
        """
        Helper function to recv n bytes or return None if EOF is hit
        Wait for the socket to receive all data and return the full message
        """
        pass

    @abstractmethod
    def getIP(self):
        return "UNKNOWN - NOT IMPLEMENTED"

    @abstractmethod
    def getPort(self):
        return 0

    @abstractmethod
    def getPartnerIP(self):
        return "UNKNOWN - NOT IMPLEMENTED"

    @abstractmethod
    def getPartnerPort(self):
        return 0

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def who_am_i(self):
        pass

    @abstractmethod
    def who_is_my_new_friend(self):
        pass
