from typing import Callable

import pyconio
from equipments.patterns.Observing import ObserverCollection, Observer


class ConsoleContext:
    def __init__(self,
                 outlook: Callable,
                 enterOutlook: Callable = None,
                 exitOutlook: Callable = None):
        self.exit = False
        self.back = False
        self._outlook = outlook
        if self._outlook is None:
            self._outlook = self._defaultOutlook
        self._enterOutlook = enterOutlook
        self._exitOutlook = exitOutlook
        self._observing = ObserverCollection()
        self._observing.add(-1, "exit")
        self._observing.add(0, "back")

        self._observing.get(-1).subscribe(lambda: setattr(self, "exit", True))
        self._observing.get(0).subscribe(lambda: setattr(self, "back", True))

    def __enter__(self):
        pyconio.clrscr()
        if self._enterOutlook is not None:
            self._enterOutlook()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._exitOutlook is not None:
            self._exitOutlook()
        pass

    def _defaultOutlook(self):
        print(f"Not defined outlook for {self} context yet!!!")

    def getObserverCollection(self):
        return self._observing

    def loop(self):
        while not self.back and not self.exit:
            self._outlook()
            try:
                choice = int(input("Choice: "))
                if not self._observing.fire(choice):
                    print("Invalid choice")
            except ValueError:
                print("Invalid choice")
