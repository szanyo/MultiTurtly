from definitions.TurtlyDataKeys import TurtlyDataKeys
from player.AbstractPlayer import AbstractPlayer


class ServerSidePlayer(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tcp_client = kwargs.get(TurtlyDataKeys.PLAYER_TCP_CLIENT_CONNECTION.value, None)
