from turtle import tracer, Turtle, Screen
from tkinter.font import Font
from graphics.Box import Box

class TextBox(Box):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._text = kwargs.get("text", "")
        self._text_color = kwargs.get("text_color", "white")
        self._font_name = kwargs.get("font_name", 'Arial')
        self._font_size = kwargs.get("font_size", 24)
        self._font_type = kwargs.get("font_type", "normal")
        self._horizontal_alignment = kwargs.get("horizontal_alignment", "center")
        self._vertical_alignment = kwargs.get("vertical_alignment", "center")

        self._padding = kwargs.get("padding", 0)

        self._show_border = kwargs.get("show_border", False)

        self._text_width = 0
        self._text_height = 0

        self._calculate_text_size()

    @property
    def Text(self):
        return self._text

    @Text.setter
    def Text(self, value):
        self._text = value
        self._calculate_text_size()

    @property
    def TextColor(self):
        return self._text_color

    @TextColor.setter
    def TextColor(self, value):
        self._text_color = value

    @property
    def FontName(self):
        return self._font_name

    @FontName.setter
    def FontName(self, value):
        self._font_name = value
        self._calculate_text_size()

    @property
    def FontSize(self):
        return self._font_size

    @FontSize.setter
    def FontSize(self, value):
        self._font_size = value
        self._calculate_text_size()

    @property
    def FontType(self):
        return self._font_type

    @FontType.setter
    def FontType(self, value):
        self._font_type = value
        self._calculate_text_size()

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

    @property
    def Padding(self):
        return self._padding

    @Padding.setter
    def Padding(self, value):
        self._padding = value

    @property
    def ShowBorder(self):
        return self._show_border

    @ShowBorder.setter
    def ShowBorder(self, value):
        self._show_border = value

    def _calculate_text_size(self):
        # Create a Font object
        tk_font = Font(family=self._font_name, size=self._font_size, weight=self._font_type)

        # Measure the text width and height
        text_width = Screen().getcanvas().create_text(0, 0, text=self._text, font=tk_font, anchor="nw")
        bbox = Screen().getcanvas().bbox(text_width)
        self._text_width = bbox[2] - bbox[0]
        self._text_height = bbox[3] - bbox[1]

        # print(self._text, self._font_name, self._font_size, self._font_type)
        # print(self._text_width, self._text_height)

    def paint(self):
        if self._show_border:
            super().paint()

        if self._text_width > self._width - 2 * self._padding:
            print("Warning: TextBox's text width is bigger than the TextBox's width!")
        elif self._text_height > self._height - 2 * self._padding:
            print("Warning: TextBox's text height is bigger than the TextBox's height!")
        else:
            self._turtle = Turtle()
            tracer(False)
            self._turtle.speed(0)
            self._turtle.hideturtle()
            self._turtle.penup()
            self._turtle.goto(self._x, self._y - self._text_height / 2)
            self._turtle.color(self._text_color)
            self._turtle.write(self._text, move=False, align=self._horizontal_alignment, font=(self._font_name, self._font_size, self._font_type))
            tracer(True)

        # self._turtle.goto(-100, 200)
        # for step in range(15):
        #     self._turtle.write(step, align='center')
        #     self._turtle.right(90)
        #     self._turtle.forward(10)
        #     self._turtle.pendown()
        #     self._turtle.forward(160)
        #     self._turtle.penup()
        #     self._turtle.backward(170)
        #     self._turtle.left(90)
        #     self._turtle.forward(20)
        #
        # self._turtle.goto(200, 250)
        # self._turtle.write("FinishLine", align='center')
        # self._turtle.pendown()
        # self._turtle.right(90)
        # self._turtle.forward(300)
