import threading
from threading import Thread
from time import sleep
from turtle import Screen, mainloop, Turtle

from graphics.Graphics import Graphics, GraphicsCommands
from netturtle.ClientSideNetTurtle import ClientSideNetTurtle

score = 0
exit = False

def game_loop(turtle):
    global score, exit

    while not exit:
        turtle.move_forward()
        score += 1
        print(score)
        if score == 100:
            exit = True
            break
        sleep(1 - score / 100)


def exit_loop():
    global exit
    exit = True


if __name__ == "__main__":
    with Graphics() as g:

        t = ClientSideNetTurtle()
        t.updateTurtle()

        oc = Graphics().ObserverCollection
        oc.get(GraphicsCommands.LEFT).subscribe(t.turn_left)
        oc.get(GraphicsCommands.RIGHT).subscribe(t.turn_right)
        oc.get(GraphicsCommands.ESCAPE).subscribe(exit_loop)
        oc.get(GraphicsCommands.FORWARD).subscribe(t.move_forward)
        oc.get(GraphicsCommands.UPDATE_ALL).subscribe(t.updateTurtle)

        _empty_movement_thread = threading.Thread(target=t.empty_movement_loop)
        _empty_movement_thread.start()

        game_thread = Thread(target=game_loop, args=(t,))
        game_thread.start()

        # Start the netturtle's event loop
        mainloop()

        game_thread.join()

        print("Done")
        print("Close the window to exit.")

        quit()