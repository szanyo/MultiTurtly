from room.AbstractRoom import AbstractRoom


class ServerSideGameRoom(AbstractRoom):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

