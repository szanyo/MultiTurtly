import threading
from enum import auto
from time import sleep, time
from turtle import Screen, done, speed, isvisible, hideturtle, up, goto, down, isdown, showturtle, pendown, penup, fd, \
    circle, color

from equipments.patterns.Observing import ObserverCollection
from graphics.GUI import GUI


class GraphicsCommands:
    LEFT = auto()
    RIGHT = auto()
    FORWARD = auto()
    BACKWARD = auto()
    ESCAPE = auto()
    PAUSE = auto()

    UPDATE_ALL = auto()


class Graphics:
    _graphics = None

    def __new__(cls, *args, **kwargs):
        if cls._graphics is None:
            cls._graphics = super().__new__(cls, *args, **kwargs)
        return cls._graphics

    def __init__(self, *args, **kwargs):
        self._active = True
        self._old_width = 0
        self._old_height = 0

        self._wnd = None
        self._observer_collection = ObserverCollection()
        self._initEvents()
        self.initialize()

        self._gui = GUI(self)
        self._gui.paint()

        self._observer_collection.get(GraphicsCommands.UPDATE_ALL).subscribe(self._update_gui)

        self._onScreenResizeListenerThread = threading.Thread(target=self._onScreenResizeListener)
        self._onScreenResizeListenerThread.start()

    def initialize(self):
        self._wnd = Screen()
        self._wnd.colormode(255)
        # self._wnd.setup(800, 600)
        self._wnd.title("MultiTurtly")
        self._wnd.bgcolor("black")

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

        self._wnd.onkey(lambda: self._observer_collection.fire(GraphicsCommands.UPDATE_ALL), "r")

        self._wnd.listen()

    def _initEvents(self):
        self._observer_collection.add(GraphicsCommands.LEFT, "turtle_turn_left")
        self._observer_collection.add(GraphicsCommands.RIGHT, "turtle_turn_right")
        self._observer_collection.add(GraphicsCommands.FORWARD, "turtle_move_forward")
        self._observer_collection.add(GraphicsCommands.BACKWARD, "turtle_move_backward")
        self._observer_collection.add(GraphicsCommands.ESCAPE, "turtle_exit")
        self._observer_collection.add(GraphicsCommands.PAUSE, "turtle_pause")

        self._observer_collection.add(GraphicsCommands.UPDATE_ALL, "update_all")

    def _update_gui(self):
        self.clear()
        self.initialize()
        self._gui.update()
        self._gui.paint()

    def _onScreenResizeListener(self):
        self._old_width = self._wnd.window_width()
        self._old_height = self._wnd.window_height()
        while self._active:
            if self._old_width != self._wnd.window_width() or self._old_height != self._wnd.window_height():
                while self._old_width != self._wnd.window_width() or self._old_height != self._wnd.window_height():
                    self._old_width = self._wnd.window_width()
                    self._old_height = self._wnd.window_height()
                    sleep(0.25)
                self._observer_collection.fire(GraphicsCommands.UPDATE_ALL)
            sleep(0.25)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._active = False
        done()
        if self._wnd is not None:
            self._wnd.bye()

    def clear(self):
        if self._wnd is not None:
            self._wnd.clear()

    @property
    def Window(self):
        return self._wnd

    @property
    def GUI(self):
        return self._gui

    @property
    def ObserverCollection(self):
        return self._observer_collection
