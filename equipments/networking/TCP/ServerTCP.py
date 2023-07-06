#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.10"
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"

import pickle
import struct
from threading import Thread

from _socket import SO_REUSEADDR, SOL_SOCKET

from equipments.networking import Networking
from equipments.networking.Networking import ControlCommands, NetworkingEvents, inform
from equipments.networking.TCP.AbstractTCP import AbstractTCP
from equipments.security.Cryptography import Cryptography


class Server(Thread, AbstractTCP):
    """Server class for TCP connection"""

    def __init__(self, **kwargs):
        """
        Constructor of the Server class

        :param server_ip: IP address of the server
        :param server_port: Port of the server
        :param mode: Mode of the connection (default: TransferMode.COMPLEX)
            (Complex consumes unlimited size of data in one message,
            Simple consumes only 1024 bytes of data in one message)
        :param security_crypt: Cryptography object for encrypting and decrypting the message data (default: Crypt())
        """
        Thread.__init__(self)
        AbstractTCP.__init__(self, **kwargs)

        self._client_connection = None  # the client connection object

        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # set the socket options
        try:
            self._socket.bind(self._server_address)  # bind the socket to the server address
        except OSError as e:
            print(e)
            self._socket.close()
            input("Press enter to exit...")
        self._socket.listen(1)  # listen for incoming connections

    def _control_connection_is_not_alive(self, *args, **kwargs):
        inform(Networking.SHW, "CONTROL_CONNECTION_IS_NOT_ALIVE", args)
        self._connected = False
        self.event_handlers.fire(NetworkingEvents.DISCONNECTED)
        if self._client_connection is not None:
            self._client_connection.close()
            self._client_connection = None
        # Try to reconnect
        self.open_for_new_connection()

    def run(self):
        """
        Run the server
        Main loop of the server thread
        """
        self.open_for_new_connection()
        while not self._close:
            try:
                if not self._connected or not self.catch():
                    self._check_connection()
            except ConnectionResetError as e:
                self.event_handlers.fire(
                    NetworkingEvents.RESET,
                    "server/run/reset", e)
            except ConnectionAbortedError as e:
                self.event_handlers.fire(
                    NetworkingEvents.ABORTED,
                    "server/run/abort", e)

    def close(self):
        """Close the server connection"""
        try:
            self._close = True
            self.send(ControlCommands.CLOSE)
            self._client_connection.close()
            self._socket.close()
        finally:
            pass
        self.event_handlers.fire(
            NetworkingEvents.CLOSED,
            "server/close/closed")

    def open_for_new_connection(self):
        """Wait for a connection request from a client"""
        self.event_handlers.fire(
            NetworkingEvents.WAITING_FOR_NEW_CONNECTION,
            "server/open_for_new_connection/waiting")
        try:
            self._client_connection, self._client_address = self._socket.accept()
        except Exception as e:
            self._connected = False
            self.event_handlers.fire(NetworkingEvents.DISCONNECTED)
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "server/open_for_new_connection/refused", e)
            return False
        self.event_handlers.fire(
            NetworkingEvents.CREATED,
            "server/open_for_new_connection/created")
        self._control_command_handlers.fire(ControlCommands.CHECK_CONNECTION)
        return True

    def is_connected(self):
        """
        Check if the client is connected to the server
        :return: True if connected, False if not
        """
        if self._connected and self._client_connection is not None:
            return True
        else:
            return False

    # def _send_simple(self, msg):
    #     """
    #     Send message to the client in simple mode
    #     :param msg: Message to send
    #     """
    #     msg = pickle.dumps(msg)
    #     try:
    #         if self._security_crypt is not None and isinstance(self._security_crypt, Crypt):
    #             self._client_connection.sendall(self._security_crypt.encrypt(msg))
    #         else:
    #             self._client_connection.sendall(bytes(msg))
    #     except OSError as e:
    #         self.event_handlers.fire(NetworkingEvents.REFUSED, e, "server/send_simple/refused")

    # def _catch_simple(self):
    #     """
    #     Catch message from the client in simple mode
    #     :return: True if caught valid message, False if not
    #     """
    #     data = self._client_connection.recv(1024)
    #     if data is not None:
    #         if self._security_crypt is not None and isinstance(self._security_crypt, Crypt):
    #             msg = self._security_crypt.decrypt(data)
    #         else:
    #             # TODO WARNING: potential error location (bytes to str)
    #             msg = data
    #         if is_pickle_stream(msg):
    #             # TODO: pickle.loads() missing maybe?
    #             if isinstance(msg, ControlCommands):
    #                 self._control_command_handlers.fire(msg, "server/catch_simple/controlcommands")
    #             else:
    #                 self._queue.put(msg)
    #             return True
    #     return False

    def _send_complex(self, msg):
        """
        Send message to the client in complex mode
        :param msg: Message to send
        """
        msg = pickle.dumps(msg)
        if self._security_crypt is not None and isinstance(self._security_crypt, Cryptography):
            msg = self._security_crypt.encrypt(msg)
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            self._client_connection.sendall(msg)
        except OSError as e:
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "server/send_complex/refused", e)

    def _catch_complex_full_msg(self, n):
        """
        Helper function to recv n bytes or return None if EOF is hit
        Wait for the socket to receive all data and return the full message
        """
        data = bytearray()
        while len(data) < n:
            try:
                packet = self._client_connection.recv(n - len(data))
            except OSError as e:
                self.event_handlers.fire(
                    NetworkingEvents.REFUSED,
                    "server/catch_complex_full_msg/refused", e)
                return None
            if not packet:
                return None
            data.extend(packet)
        return data

    def who_am_i(self):
        print(120 * "-")
        print("I'm a SERVER.")
        print("SERVER_IP: " + str(self._server_address[0]))
        print("SERVER_PORT: " + str(self._server_address[1]))
        print()

    def who_is_my_new_friend(self):
        print(120 * "-")
        print("My new FRIEND ( CLIENT ) is:")
        print("CLIENT_IP: " + str(self._client_address[0]))
        print("CLIENT_PORT: " + str(self._client_address[1]))
        print()

    def getIP(self):
        return self._server_address[0]

    def getPort(self):
        return self._server_address[1]

    def getPartnerIP(self):
        return self._client_address[0]

    def getPartnerPort(self):
        return self._client_address[1]
