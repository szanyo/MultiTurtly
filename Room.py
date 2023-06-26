class Room:
    def __init__(self):
        self._netTurtles = []

    def addNetTurtle(self, netTurtle):
        self._netTurtles.append(netTurtle)