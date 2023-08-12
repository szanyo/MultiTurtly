from threading import Thread
from time import sleep
from turtle import Screen, mainloop

from netturtle.ClientSideNetTurtle import ClientSideNetTurtle

score = 0
exit = False
wnd = Screen()
t = ClientSideNetTurtle(**{"wnd": wnd})

def game_loop():
    global score, exit, t

    while not exit:
        t.move_forward()
        score += 1
        if score == 100:
            exit = True
            break
        sleep(2)


def exit_loop():
    global exit, wnd, t
    exit = True
    wnd.bye()


if __name__ == "__main__":
    wnd.setup(1024, 768)
    wnd.title("MultiTurtly")
    wnd.bgcolor("black")

    # speed()
    # penup()
    # goto(0, wnd.window_height() / 2 - 40)
    # color('white')
    # msg = "Press any key to start, if you ready!"
    # hideturtle()
    # write(msg, align='center', font=('Arial', 24, 'normal'))

    # goto(-100, 200)
    # for step in range(15):
    #     write(step, align='center')
    #     right(90)
    #     forward(10)
    #     pendown()
    #     forward(160)
    #     penup()
    #     backward(170)
    #     left(90)
    #     forward(20)
    #
    # goto(200, 250)
    # write("FinishLine", align='center')
    # pendown()
    # right(90)
    # forward(300)

    wnd.onkey(t.turn_left, "q")
    wnd.onkey(t.turn_right, "e")
    wnd.onkey(t.turn_left, "Left")
    wnd.onkey(t.turn_right, "Right")
    wnd.onkey(exit_loop, "Escape")

    wnd.listen()

    t.updateWindowSize()

    game_thread = Thread(target=game_loop)
    game_thread.start()

    # Start the netturtle's event loop
    mainloop()

    game_thread.join()

    print("Done")
    print("Close the window to exit.")

    quit()
