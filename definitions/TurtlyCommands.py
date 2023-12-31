from enum import auto, Enum


class TurtlyCommands:
    DEFAULT = auto()


class TurtlyCommandsType(Enum):
    REQUEST = auto()
    RESPONSE = auto()


class TurtlyServerCommands(TurtlyCommands, Enum):
    NEW_PLAYER_REGISTRATION = auto()
    REMOVE_PLAYER = auto()
    OPEN_NEW_GAME_ROOM = auto()
    LIST_GAME_ROOMS = auto()
    JOIN_TO_GAME_ROOM = auto()
    CLOSE_GAME_ROOM = auto()
    IDENTIFICATION = auto()


class TurtlyGameRoomCommands(TurtlyCommands, Enum):
    READY_TO_PLAY = auto()
    START_GAME = auto()
    INITIALIZATION = auto()
    IDENTIFICATION = auto()
    SYNC = auto()
    TURN_LEFT = auto()
    TURN_RIGHT = auto()
    MOVE_FORWARD = auto()
    PAUSE = auto()
    ESCAPE = auto()


class TurtlyClientCommands(TurtlyCommands, Enum):
    NEW_PLAYER_REGISTRATION = auto()
    LIST_GAME_ROOMS = auto()
    OPEN_NEW_GAME_ROOM = auto()
    JOIN_TO_GAME_ROOM = auto()
