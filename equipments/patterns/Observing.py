#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.8 "
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"

from typing import Callable


class Observer:
    def __init__(self, name="Anonymous"):
        self._name = name
        self._callbacks = []

    def get_name(self):
        return self._name

    def subscribe(self, observable: Callable):
        self._callbacks.append(observable)

    def unsubscribe(self, observable: Callable):
        self._callbacks.remove(observable)

    def fire(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class GlobalObservers:
    _events: dict[any, Observer] = {}

    @staticmethod
    def add(event, name="Anonymous"):
        GlobalObservers._events[event] = Observer(name)

    @staticmethod
    def remove(event):
        GlobalObservers._events.pop(event)

    @staticmethod
    def get(event):
        return GlobalObservers._events[event]


class ObserverCollection:
    def __init__(self):
        self._events: dict[any, Observer] = {}

    def add(self, event, name="Anonymous"):
        self._events[event] = Observer(name)

    def remove(self, event):
        self._events.pop(event)

    def get(self, event):
        return self._events[event]

    def fire(self, event, *args, **kwargs):
        if event in self._events:
            self._events[event].fire(*args, **kwargs)
            return True
        return False

    def fire_all(self, *args, **kwargs):
        for event in self._events.values():
            event.fire(*args, **kwargs)
