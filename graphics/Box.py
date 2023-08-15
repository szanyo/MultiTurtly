from turtle import speed, hideturtle, color, up, goto, down, fd, circle, update, tracer, isvisible, showturtle, Turtle


class Box:
    def __init__(self, x=0, y=0, width=100, height=100, radius=20, paintcolor="white"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.radius = radius
        self.paintcolor = paintcolor

    def paint(self):
        temp_turtle = Turtle()
        temp_turtle.speed(0)
        temp_turtle.hideturtle()
        temp_turtle.color(self.paintcolor)
        tracer(0, 0)
        temp_turtle.up()
        temp_turtle.goto(self.x - self.width / 2 + self.radius,
                         self.y - self.height / 2)
        temp_turtle.down()
        for _ in range(2):
            temp_turtle.fd(self.width - 2 * self.radius)
            temp_turtle.circle(self.radius, 90)
            temp_turtle.fd(self.height - 2 * self.radius)
            temp_turtle.circle(self.radius, 90)
        try:
            update()
        except:
            pass
