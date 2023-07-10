from AbstractRoom import AbstractRoom


class ClientSideGameRoom(AbstractRoom):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)