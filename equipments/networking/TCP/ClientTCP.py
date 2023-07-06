#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.10"
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"

import pickle
import struct
import time
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

from equipments.networking import Networking
from equipments.networking.Networking import ControlCommands, inform
from equipments.networking.Networking import NetworkingEvents
from equipments.networking.TCP.AbstractTCP import AbstractTCP
from equipments.security.Cryptography import Cryptography


class Client(Thread, AbstractTCP):
    """Client class for TCP connection"""

    def __init__(self, **kwargs):
        """
        Constructor of the Client class

        :param server_ip: IP address of the server (default: localhost)
        :param server_port: Port of the server (default: 5051)
        :param mode: Mode of the connection (default: TransferMode.COMPLEX)
            (Complex consumes unlimited size of data in one message,
            Simple consumes only 1024 bytes of data in one message)
        :param security_crypt: Cryptography object for encrypting and decrypting the message data (default: Crypt())
        """
        Thread.__init__(self)
        AbstractTCP.__init__(self, **kwargs)
        if kwargs.get("socket") is not None:
            self._socket = kwargs["socket"]
            self._server_address = ("ANONYMOUS_CLIENT_IP", "ANONYMOUS_CLIENT_PORT")
            self._client_address = (kwargs["client_ip"], kwargs["client_port"])
            self._connected = True

    def _control_connection_is_not_alive(self, *args, **kwargs):
        inform(Networking.SHW, "CONTROL_CONNECTION_IS_NOT_ALIVE", args)
        if not self._close:
            self._connected = False
            kwargs = {"partner": self}
            self.event_handlers.fire(NetworkingEvents.DISCONNECTED, **kwargs)
            # Try to reconnect
            self.connect()

    def run(self):
        """
        Run the client
        Main loop of the client thread
        """
        while not self._close:
            try:
                if not self._connected or not self.catch():
                    self._check_connection()
            except ConnectionAbortedError as e:
                self.event_handlers.fire(
                    NetworkingEvents.ABORTED,
                    "client/run/abort", e)
            except ConnectionResetError as e:
                self.event_handlers.fire(
                    NetworkingEvents.RESET,
                    "client/run/reset", e)

    def close(self):
        """Close the client connection"""
        try:
            self._close = True
            self.send(ControlCommands.CLOSE)
            self._socket.close()
        finally:
            pass
        kwargs = {"partner": self}
        self.event_handlers.fire(
            NetworkingEvents.CLOSED,
            "client/close/closed",
            **kwargs)

    def connect(self):
        """Connect to the server"""
        if self._connected:
            self._control_command_handlers.fire(ControlCommands.CHECK_CONNECTION)
            return True
        try:
            self._socket = socket(AF_INET, SOCK_STREAM)
            self._socket.connect(self._server_address)
        except TypeError as e:
            return False
        except ConnectionRefusedError as e:
            self._connected = False
            kwargs = {"partner": self}
            self.event_handlers.fire(NetworkingEvents.DISCONNECTED, **kwargs)
            time.sleep(2)
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "client/connect/refused", e)
            return False
        except OSError as e:
            time.sleep(2)
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "client/connect/refused", e)
            return False
        self._client_address = self._socket.getsockname()
        self.event_handlers.fire(
            NetworkingEvents.CREATED,
            "client/connect/created")
        self._control_command_handlers.fire(ControlCommands.CHECK_CONNECTION)
        return True

    # def _send_simple(self, msg):
    #     """
    #     Send simple message to the server
    #     :param msg: Message to send
    #     """
    #     msg = pickle.dumps(msg)
    #     try:
    #         if self._security_crypt is not None and isinstance(self._security_crypt, Crypt):
    #             self._socket.sendall(self._security_crypt.encrypt(msg))
    #         else:
    #             self._socket.sendall(bytes(msg))
    #     except OSError as e:
    #         self.event_handlers.fire(NetworkingEvents.REFUSED, e, "client/send_simple/refused")

    # def _catch_simple(self):
    #     """
    #     Catch simple message from the server
    #     :return: True if caught valid message, False if not
    #     """
    #     data = self._socket.recv(1024)
    #     if data is not None:
    #         if self._security_crypt is not None and isinstance(self._security_crypt, Crypt):
    #             msg = self._security_crypt.decrypt(data)
    #         else:
    #             # TODO WARNING: potential error location (bytes to string)
    #             msg = data
    #         if is_pickle_stream(msg):
    #             # TODO: pickle.loads() missing maybe?
    #             if isinstance(msg, ControlCommands):
    #                 self._control_command_handlers.fire(msg, "client/catch_simple/controlcommands")
    #             else:
    #                 self._queue.put(msg)
    #             return True
    #     return False

    def _send_complex(self, msg):
        """
        Send complex message to the server
        :param msg: Message to send
        """
        msg = pickle.dumps(msg)
        if self._security_crypt is not None and isinstance(self._security_crypt, Cryptography):
            msg = self._security_crypt.encrypt(msg)
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            self._socket.sendall(msg)
        except OSError as e:
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "client/send_complex/refused", e)

    def _catch_complex_full_msg(self, n):
        """
        Helper function to recv n bytes or return None if EOF is hit
        Wait for the socket to receive all data and return the full message
        """
        data = bytearray()
        while len(data) < n:
            try:
                packet = self._socket.recv(n - len(data))
            except OSError as e:
                self.event_handlers.fire(
                    NetworkingEvents.REFUSED,
                    "client/catch_complex_full_msg/refused", e)
                return None
            if not packet:
                return None
            data.extend(packet)
        return data

    def who_am_i(self):
        print(120 * "-")
        print("I'm a CLIENT.")
        print("CLIENT_IP: " + str(self._client_address[0]))
        print("CLIENT_PORT: " + str(self._client_address[1]))
        print()

    def who_is_my_new_friend(self):
        print(120 * "-")
        print("My new FRIEND ( SERVER ) is:")
        print("SERVER_IP: " + str(self._server_address[0]))
        print("SERVER_PORT: " + str(self._server_address[1]))
        print()

    def getIP(self):
        return self._client_address[0]

    def getPort(self):
        return self._client_address[1]

    def getPartnerIP(self):
        return self._server_address[0]

    def getPartnerPort(self):
        return self._server_address[1]
