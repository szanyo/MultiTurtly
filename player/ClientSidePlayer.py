from player.AbstractPlayer import AbstractPlayer


class ClientSidePlayer(AbstractPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)