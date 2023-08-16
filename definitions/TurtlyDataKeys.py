from enum import Enum, auto


class TurtlyDataKeys(Enum):

    # Room
    GAME_ROOM_PLAYERS_NAMES = "game_room_players_names"
    GAME_ROOM_PLAYERS_UUIDS = "game_room_players_uuids"
    GAME_ROOM_ADMIN_NAME = "game_room_admin_name"
    GAME_ROOM_ADMIN_UUID = "game_room_admin_uuid"
    GAME_ROOM_ADMIN = "game_room_admin"
    GAME_ROOM_NAME = "game_room_name"
    GAME_ROOM_UUID = "game_room_uuid"
    GAME_ROOM_LOCKED = "game_room_locked"
    GAME_ROOM_CLOSED = "game_room_closed"
    GAME_ROOM_STARTED = "game_room_started"
    GAME_ROOM_PLAYERS_REPRESENTATION = "game_room_players_representation"
    GAME_ROOM = "game_room"
    GAME_ROOMS = "game_rooms"

    # Player
    PLAYER_NAME = "player_name"
    PLAYER_UUID = "player_uuid"
    PLAYER_COLOR = "player_color"
    PLAYER_INITIAL_POSITION = "player_initial_position"
    PLAYER_INITIAL_DIRECTION = "player_initial_direction"
    PLAYER_READY = "player_ready"
    PLAYER = "player"

    # Connections
    SERVER_SIDE_PLAYER_TCP_CONNECTION = "server_side_player_tcp_connection"
    CLIENT_SIDE_GAME_ROOM_TCP_CONNECTION = "client_side_game_room_tcp_connection"
