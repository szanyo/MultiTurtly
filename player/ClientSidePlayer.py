from player.AbstractPlayer import AbstractPlayer


class ClientSidePlayer(AbstractPlayer):
    def __init__(self, name, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.color = color