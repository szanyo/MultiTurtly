import asyncio
import time

from ConsoleContext import ConsoleContext
from Player import Player
from TurtlyClient import TurtlyClient


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
        print("Game room name: ")
        name = input()
        self._tc.createRoom(name)
        self._tc.updateInfo()
        self._ready_to_start_game()

    def _join_to_game_room(self):
        pass

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


if __name__ == "__main__":
    print("Welcome to Turtly!")
    print("Connecting to server...")
    console = Console()
    console.main_loop()
