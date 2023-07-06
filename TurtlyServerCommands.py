from enum import auto, Enum


class TurtlyServerCommands(Enum):
    OPEN_NEW_GAME_ROOM = auto()
    LIST_GAME_ROOMS = auto()
    JOIN_TO_GAME_ROOM = auto()
    CLOSE_GAME_ROOM = auto()
    IDENTIFICATION = auto()


class TurtlyGameRoomCommands(Enum):
    READY_TO_PLAY = auto()
    START_GAME = auto()
    IDENTIFICATION = auto()


class TurtlyClientCommands(Enum):
    GAME_ROOM_LIST = auto()
