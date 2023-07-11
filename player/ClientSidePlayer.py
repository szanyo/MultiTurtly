from definitions.TurtlyDataKeys import TurtlyDataKeys
from netturtle.ClientSideNetTurtle import ClientSideNetTurtle
from player.AbstractPlayer import AbstractPlayer


class ClientSidePlayer(AbstractPlayer, ClientSideNetTurtle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

