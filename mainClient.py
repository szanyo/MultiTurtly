import asyncio
import time
from threading import Thread

from graphics.Graphics import Graphics
from room.AbstractGameRoom import roomNameValidator
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

        self._tc.createRoom(created_room_name)
        self._tc.updateInfo()
        self._ready_to_start_game()

    def _join_to_game_room(self):
        joined = False
        while not joined:
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
                self._tc.updateInfo()
                self._ready_to_start_game()
                joined = True
            else:
                print("Room not found!")
                joined = False

    def _ready_to_start_game(self):
        print("---Ready to start game---")
        print("Press any key to start game")
        input()
        self._tc.readyToPlay()
        self._game_loop_info()

    def _game_loop_info(self):
        print("---Game loop info---")
        while True:
            self._tc.updateInfo()
            time.sleep(5)


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
        Thread(target=console.main_loop).start()
        graphics.Window.mainloop()
