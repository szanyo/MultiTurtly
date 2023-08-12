import os

from equipments.platform.System import System
from turtly.TurtlyServer import TurtlyServer

if __name__ == "__main__":
    # if not System.is_user_admin():
    #     System.get_admin_priv()
    ts = TurtlyServer()
    ts.start()

    ts.join()