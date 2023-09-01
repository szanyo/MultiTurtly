from graphics.Box import Box


class TextBox(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._text = kwargs.get("text", "")
        self._text_color = kwargs.get("text_color", "white")
        self._font = kwargs.get("font", ('Arial', 24, 'normal'))
        self._horizontal_alignment = kwargs.get("horizontal_alignment", "center")
        self._vertical_alignment = kwargs.get("vertical_alignment", "center")
    @property
    def Text(self):
        return self._text

    @Text.setter
    def Text(self, value):
        self._text = value

    @property
    def TextColor(self):
        return self._text_color

    @TextColor.setter
    def TextColor(self, value):
        self._text_color = value

    @property
    def Font(self):
        return self._font

    @Font.setter
    def Font(self, value):
        self._font = value

    @property
    def HorizontalAlignment(self):
        return self._horizontal_alignment

    @HorizontalAlignment.setter
    def HorizontalAlignment(self, value):
        self._horizontal_alignment = value

    @property
    def VerticalAlignment(self):
        return self._vertical_alignment

    @VerticalAlignment.setter
    def VerticalAlignment(self, value):
        self._vertical_alignment = value

    def paint(self):
        super().paint()

        self._turtle.speed()
        self._turtle.penup()
        self._turtle.goto(self._x + self._width / 2 - 40, self._y + 10)
        self._turtle.color(self._text_color)
        msg = "Press any key to start, if you ready!"
        self._turtle.hideturtle()
        self._turtle.write(msg, align='center', font=('Arial', 24, 'normal'))

        self._turtle.goto(-100, 200)
        for step in range(15):
            self._turtle.write(step, align='center')
            self._turtle.right(90)
            self._turtle.forward(10)
            self._turtle.pendown()
            self._turtle.forward(160)
            self._turtle.penup()
            self._turtle.backward(170)
            self._turtle.left(90)
            self._turtle.forward(20)

        self._turtle.goto(200, 250)
        self._turtle.write("FinishLine", align='center')
        self._turtle.pendown()
        self._turtle.right(90)
        self._turtle.forward(300)
