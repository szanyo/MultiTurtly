from enum import auto
from threading import Thread
from turtle import Screen

from equipments.patterns.Observing import ObserverCollection


class GraphicsCommands:
    LEFT = auto()
    RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    ESCAPE = auto()
    PAUSE = auto()


class Graphics:
    _graphics = None

    def __new__(cls, *args, **kwargs):
        if cls._graphics is None:
            cls._graphics = super().__new__(cls, *args, **kwargs)
        return cls._graphics

    def __init__(self, *args, **kwargs):
        self._wnd = Screen()
        self._wnd.setup(1024, 768)
        self._wnd.title("MultiTurtly")
        self._wnd.bgcolor("black")
        self._observer_collection = ObserverCollection()
        self._initEvents()

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.LEFT), "a")
        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.LEFT), "Left")

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.RIGHT), "d")
        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.RIGHT), "Right")

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.FORWARD), "w")
        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.FORWARD), "Up")

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.BACKWARD), "s")
        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.BACKWARD), "Down")

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.ESCAPE), "Escape")
        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.PAUSE), "p")

        self._wnd.listen()

    def _initEvents(self):
        self._observer_collection.add(GraphicsCommands.LEFT)
        self._observer_collection.add(GraphicsCommands.RIGHT)
        self._observer_collection.add(GraphicsCommands.FORWARD)
        self._observer_collection.add(GraphicsCommands.BACKWARD)
        self._observer_collection.add(GraphicsCommands.ESCAPE)
        self._observer_collection.add(GraphicsCommands.PAUSE)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._wnd.bye()

    def clear(self):
        self._wnd.clear()

    @property
    def Window(self):
        return self._wnd

    @property
    def ObserverCollection(self):
        return self._observer_collection
