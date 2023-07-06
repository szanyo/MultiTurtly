#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.8 "
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"


class Observer:
    def __init__(self, name="Anonymous"):
        self._name = name
        self._callbacks = []

    def get_name(self):
        return self._name

    def subscribe(self, observable):
        self._callbacks.append(observable)

    def unsubscribe(self, observable):
        self._callbacks.remove(observable)

    def fire(self, *args, **kwargs):
        for callback in self._callbacks:
            callback(*args, **kwargs)


class GlobalObservers:
    _observers: dict[any, Observer] = {}

    @staticmethod
    def add(observer_name, observer: Observer):
        GlobalObservers._observers[observer_name] = observer

    @staticmethod
    def remove(observer_name):
        GlobalObservers._observers.pop(observer_name)

    @staticmethod
    def get(observer_name):
        return GlobalObservers._observers[observer_name]


class ObserverCollection:
    def __init__(self):
        self._events: dict[any, Observer] = {}

    def add(self, event, observer: Observer):
        self._events[event] = observer

    def remove(self, event):
        self._events.pop(event)

    def get(self, event):
        return self._events[event]

    def fire(self, event, *args, **kwargs):
        self._events[event].fire(*args, **kwargs)

    def fire_all(self, *args, **kwargs):
        for event in self._events.values():
            event.fire(*args, **kwargs)
