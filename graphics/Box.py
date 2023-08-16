from turtle import speed, hideturtle, color, up, goto, down, fd, circle, update, tracer, isvisible, showturtle, Turtle


class Box:
    def __init__(self, x=0, y=0, width=100, height=100, radius=20, paintcolor="white"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.paintcolor = paintcolor

        self._turtle = Turtle()

    def paint(self):
        self._turtle = Turtle()
        self._turtle.speed(0)
        self._turtle.hideturtle()
        self._turtle.color(self.paintcolor)
        tracer(False)
        self._turtle.up()
        self._turtle.goto(self.x - self.width / 2 + self.radius,
                         self.y - self.height / 2)
        self._turtle.down()
        for _ in range(2):
            self._turtle.fd(self.width - 2 * self.radius)
            self._turtle.circle(self.radius, 90)
            self._turtle.fd(self.height - 2 * self.radius)
            self._turtle.circle(self.radius, 90)
        tracer(True)
