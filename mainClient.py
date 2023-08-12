import asyncio
import time
from threading import Thread
from turtle import mainloop

import pyconio
from graphics.Graphics import Graphics
from room.AbstractGameRoom import roomNameValidator
from room.ClientSideGameRoom import ClientSideGameRoomEvents
from turtly.ConsoleContext import ConsoleContext
from turtly.TurtlyClient import TurtlyClient


class Console:
    def __init__(self):
        self._tc = TurtlyClient()
        self._tc.start()
        asyncio.run(self._tc.until_connection_has_become_alive())  # wait for the first live network connection

    def main_loop(self):
        print("Connected to server!")

        print("Please enter your username!")
        print("Player username: ")
        self._tc.registerPlayer(input())

        mainContext = ConsoleContext(self._print_main_menu)

        mainContext.getObserverCollection().add(1, "create_new_game_room")
        mainContext.getObserverCollection().add(2, "join_to_game_room")

        mainContext.getObserverCollection().get(1).subscribe(self._create_new_game_room)
        mainContext.getObserverCollection().get(2).subscribe(self._join_to_game_room)

        with mainContext as context:
            context.loop()

        self._tc.close()
        self._tc.join()

    def _create_new_game_room(self):
        created = False
        while not created:
            pyconio.clrscr()
            print("---Create new game room---")
            created_room_name = ""
            while created_room_name == "":
                self._print_create_controller()
                created_room_name = input()

                if created_room_name == "0":
                    return
                elif created_room_name == "-1":
                    exit()

                if not roomNameValidator(created_room_name):
                    created_room_name = ""
                    print("Invalid room name!")

            self._tc.updateRoomList()
            asyncio.run(self._tc.until_room_list_updated())

            if self._tc.createRoom(created_room_name):
                self._tc.sync()
                self._ready_to_start_game()
                created = True
            else:
                print("Room already exists!")
                created = False

    def _join_to_game_room(self):
        joined = False
        while not joined:
            pyconio.clrscr()
            print("---Join to game room---")
            selected_room_name = ""
            while selected_room_name == "":
                print("Game room list:")
                self._tc.updateRoomList()
                asyncio.run(self._tc.until_room_list_updated())
                self._print_join_contoller()
                selected_room_name = input()

                if selected_room_name == "0":
                    return
                elif selected_room_name == "-1":
                    exit()
                if not roomNameValidator(selected_room_name):
                    selected_room_name = ""

            if self._tc.joinRoom(selected_room_name):
                self._tc.sync()
                self._ready_to_start_game()
                joined = True
            else:
                print("Room not found!")
                joined = False

    def _ready_to_start_game(self):
        """Wait for admin player to start game"""

        # Subscribe to room update event that will be redrawing the screen
        self._tc.Room.EventHandler.get(ClientSideGameRoomEvents.UPDATE).subscribe(self._on_update_room)
        self._on_update_room()

        # Wait for player to press any key to send ready signal
        input()

        # Unsubscribe from room update event
        self._tc.Room.EventHandler.get(ClientSideGameRoomEvents.UPDATE).unsubscribe(self._on_update_room)

        # Subscribe to room update event that will be redrawing the screen after ready signal
        # This time the screen will be different because the player is ready and waiting for other players
        self._tc.Room.EventHandler.get(ClientSideGameRoomEvents.UPDATE).subscribe(self._on_update_room_ready)

        self._tc.readyToPlay()

        # Wait for admin player to start game
        if self._tc.isAdmin():
            while True:
                input()
                if all(player.Ready for player in self._tc.Room.Players.values()):
                    self._tc.startGame()
                    break
                else:
                    print("Wait for other players to be ready!")
        while not self._tc.Room.Started:
            time.sleep(0.1)

        # Unsubscribe from room update event
        self._tc.Room.EventHandler.get(ClientSideGameRoomEvents.UPDATE).unsubscribe(self._on_update_room_ready)

        self._tc.start_listening_graphic_events()
        
        # Start game loop
        self._tc.Room.gameLoop()
        
        self._tc.stop_listening_graphic_events()

        # TODO: back to game room menu

    def _on_update_room(self):
        pyconio.clrscr()
        print("---Ready to start game---")
        self._tc.Room.print_status()
        print("Press any key if you are ready to start the game")

    def _on_update_room_ready(self):
        pyconio.clrscr()
        print("---Game loop info---")
        print("Wait in lobby for other players to join...")
        print()
        self._tc.Room.print_status()
        if self._tc.isAdmin():
            print("You are the ADMIN of this game room")
            print("Press any key to start the game if everyone is ready")
        else:
            print("Wait!!!")
            print("If everyone is ready, the game will be started by ADMIN player")

    def _print_main_menu(self):
        print("---Main menu---")
        print("1: Create new game room")
        print("2: Join to game room")
        print()
        print("0: Back")
        print("-1: Exit")

    def _print_create_controller(self):
        print("0: Back")
        print("-1: Exit")
        print("enter (empty): Retry")
        print()
        print("Type room name to create:")

    def _print_join_contoller(self):
        print("0: Back")
        print("-1: Exit")
        print("enter (empty): Refresh room list")
        print()
        print("Type room name to join:")


if __name__ == "__main__":
    print("Welcome to turtly!")
    print("Connecting to server...")
    console = Console()
    with Graphics() as graphics:
        main_thread = Thread(target=console.main_loop)
        main_thread.start()
        mainloop()
        main_thread.join()
