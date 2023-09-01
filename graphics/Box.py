from turtle import speed, hideturtle, color, up, goto, down, fd, circle, update, tracer, isvisible, showturtle, Turtle


class Box:
    def __init__(self, *args, **kwargs):
        self._x = kwargs.get("x", 0)
        self._y = kwargs.get("y", 0)
        self._width = kwargs.get("width", 100)
        self._height = kwargs.get("height", 100)
        self._radius = kwargs.get("radius", 20)
        self._paintcolor = kwargs.get("paintcolor", "white")

        self._turtle = Turtle()

    @property
    def X(self):
        return self._x

    @X.setter
    def X(self, value):
        self._x = value

    @property
    def Y(self):
        return self._y

    @Y.setter
    def Y(self, value):
        self._y = value

    @property
    def Width(self):
        return self._width

    @Width.setter
    def Width(self, value):
        self._width = value

    @property
    def Height(self):
        return self._height

    @Height.setter
    def Height(self, value):
        self._height = value

    @property
    def Radius(self):
        return self._radius

    @Radius.setter
    def Radius(self, value):
        self._radius = value

    @property
    def PaintColor(self):
        return self._paintcolor

    @PaintColor.setter
    def PaintColor(self, value):
        self._paintcolor = value

    def paint(self):
        self._turtle = Turtle()
        self._turtle.speed(0)
        self._turtle.hideturtle()
        self._turtle.color(self._paintcolor)
        tracer(False)
        self._turtle.up()
        self._turtle.goto(self._x - self._width / 2 + self._radius,
                          self._y - self._height / 2)
        self._turtle.down()
        for _ in range(2):
            self._turtle.fd(self._width - 2 * self._radius)
            self._turtle.circle(self._radius, 90)
            self._turtle.fd(self._height - 2 * self._radius)
            self._turtle.circle(self._radius, 90)
        tracer(True)
