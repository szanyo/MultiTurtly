from turtle import speed, hideturtle, color, up, goto, down, fd, circle, update, tracer


class Box:
    def __init__(self, x=0, y=0, width=100, height=100, radius=20, paintcolor="white"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.paintcolor = paintcolor

    def paint(self, ):
        memento_speed = speed()

        speed(0)
        hideturtle()
        color(self.paintcolor)
        tracer(0, 0)
        up()
        goto(self.x - self.width / 2 + self.radius,
             self.y - self.height / 2)
        down()
        for _ in range(2):
            fd(self.width - 2 * self.radius)
            circle(self.radius, 90)
            fd(self.height - 2 * self.radius)
            circle(self.radius, 90)

        update()
        speed(memento_speed)
