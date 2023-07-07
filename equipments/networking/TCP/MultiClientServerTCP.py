#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.26"
__status__ = "Production"
__date__ = "2023.06.19"
__license__ = "MIT"

from socket import socket, AF_INET, SOCK_STREAM
from ssl import SOL_SOCKET
from threading import Thread

from _socket import SO_REUSEADDR

from equipments.networking import Networking
from equipments.networking.Networking import TransferMode, ControlCommands, NetworkingEvents, inform
from equipments.networking.TCP.ClientTCP import Client
from equipments.patterns.Observing import ObserverCollection, Observer


def disconnected(*args, **kwargs):
    print("Disconnected")


class MultiClientServer(Thread):
    """MultiClientServer class for TCP connection"""

    def __init__(self, **kwargs):
        """
        Constructor of the MultiClientServer class

        :param server_ip: IP address of the server
        :param server_port: Port of the server
        :param mode: Mode of the connection (default: TransferMode.COMPLEX)
            (Complex consumes unlimited size of data in one message,
            Simple consumes only 1024 bytes of data in one message)
        :param security_crypt: Cryptography object for encrypting and decrypting the message data (default: Crypt())
        """

        super().__init__()
        self._server_address = (
            str(kwargs.get("server_ip", "localhost")),
            kwargs.get("server_port", 5051))
        self._mode = kwargs.get("mode", TransferMode.COMPLEX)
        self._security_crypt = kwargs.get("security_crypt", None)
        Networking.SHW = kwargs.get("log", False)
        self._close = False

        self.client_connections = []

        # Event handlers
        self.event_handlers = ObserverCollection()
        self._init_event_handlers()

        self._socket = socket(AF_INET, SOCK_STREAM)  # the socket object
        self._socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)  # set the socket options
        try:
            self._socket.bind(self._server_address)  # bind the socket to the server address
        except OSError as e:
            print(e)
            self._socket.close()
            input("Press enter to exit...")
        self._socket.listen()  # listen for incoming connections

    def _init_event_handlers(self, *args, **kwargs):
        """
        Initialize the internal events of the client

        (External methods can be subscribed to these events
        by using the event_handlers object get(EVENT_TYPE).subscribe() method)
        """
        for eventType in NetworkingEvents:
            self.event_handlers.add(eventType, eventType.name)

        self.event_handlers.get(NetworkingEvents.CREATED).subscribe(
            self._connection_created)
        self.event_handlers.get(NetworkingEvents.CLOSED).subscribe(
            self._connection_closed)
        self.event_handlers.get(NetworkingEvents.REFUSED).subscribe(
            self._connection_refused)
        self.event_handlers.get(NetworkingEvents.WAITING_FOR_NEW_CONNECTION).subscribe(
            self._connection_waiting_for_new)

    def run(self):
        """
        Run the server
        Main loop of the server for accepting new connections
        """
        while not self._close:
            self.open_for_new_connection()

    def close(self):
        """Close the server connection"""
        self._close = True
        try:
            for client_connection in self.client_connections:
                client_connection.send(ControlCommands.CLOSE)
                client_connection.close()
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
        new_client = None
        try:
            new_client_connection, new_client_address = self._socket.accept()
            kwargs = {"server_ip": self._server_address[0],
                      "server_port": self._server_address[1],
                      "client_ip": new_client_address[0],
                      "client_port": new_client_address[1],
                      "mode": self._mode,
                      "security_crypt": self._security_crypt,
                      "socket": new_client_connection}
            new_client = Client(**kwargs)
            new_client.event_handlers.get(NetworkingEvents.CLOSED).subscribe(self._client_closed)
            new_client.event_handlers.get(NetworkingEvents.DISCONNECTED).subscribe(self._client_disconnected)
            # new_client.event_handlers.get(NetworkingEvents.DISCONNECTED).subscribe(disconnected)
            new_client.start()
            self.client_connections.append(new_client)
        except Exception as e:
            self.event_handlers.fire(
                NetworkingEvents.REFUSED,
                "server/open_for_new_connection/refused", e)
            return False
        kwargs = {"new_client": new_client}
        self.event_handlers.fire(
            NetworkingEvents.CREATED,
            "server/open_for_new_connection/created",
            **kwargs)
        return True

    def _connection_created(self, *args, **kwargs):
        """
        Internal method for handling the connection created event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_CREATED", args)
        if Networking.SHW:
            self.who_am_i()
            kwargs.get("new_client").who_is_my_new_friend()

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

    def _connection_waiting_for_new(self, *args, **kwargs):
        """
        Internal method for handling the waiting for new connection event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CONNECTION_WAITING_FOR_NEW", args)

    def _client_disconnected(self, *args, **kwargs):
        """
        Internal method for handling the client disconnected event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CLIENT_DISCONNECTED", kwargs.get("partner"), args)
        kwargs.get("partner").close()

    def _client_closed(self, *args, **kwargs):
        """
        Internal method for handling the client closed event
        :param args: error message
        :param kwargs: any other arguments
        """
        inform(Networking.SHW, "CLIENT_CLOSED", args)
        self.client_connections.remove(kwargs.get("partner"))

    def is_closed(self):
        return self._close

    def who_am_i(self):
        print(120 * "-")
        print("I'm a SERVER.")
        print("SERVER_IP: " + str(self._server_address[0]))
        print("SERVER_PORT: " + str(self._server_address[1]))
        print()

    def who_is_my_new_friends(self):
        for client_connection in self.client_connections:
            print(120 * "-")
            print("My new FRIEND ( CLIENT ) is:")
            print("CLIENT_IP: " + str(client_connection.getIP()))
            print("CLIENT_PORT: " + str(client_connection.getPort()))
            print()

    def getIP(self):
        return self._server_address[0]

    def getPort(self):
        return self._server_address[1]
