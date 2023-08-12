#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

import os
import platform
import subprocess
import sys

WINDOWS = "Windows"
LINUX = "Linux"

WIN_10 = 0
WIN_8 = 1
WIN_7 = 2
WIN_SERVER_2008 = 3
WIN_VISTA_SP1 = 4
WIN_VISTA = 5
WIN_SERVER_2003_SP2 = 6
WIN_SERVER_2003_SP1 = 7
WIN_SERVER_2003 = 8
WIN_XP_SP3 = 9
WIN_XP_SP2 = 11
WIN_XP_SP1 = 12
WIN_XP = 13

win_ver = [["WIN_10", [10, 0, 0]],
           ["WIN_8", [6, 2, 0]],
           ["WIN_7", [6, 1, 0]],
           ["WIN_SERVER_2008", [6, 0, 1]],
           ["WIN_VISTA_SP1", [6, 0, 1]],
           ["WIN_VISTA", [6, 0, 0]],
           ["WIN_SERVER_2003_SP2", [5, 2, 2]],
           ["WIN_SERVER_2003_SP1", [5, 2, 1]],
           ["WIN_SERVER_2003", [5, 2, 0]],
           ["WIN_XP_SP3", [5, 1, 3]],
           ["WIN_XP_SP2", [5, 1, 2]],
           ["WIN_XP_SP1", [5, 1, 1]],
           ["WIN_XP", [5, 1, 0]]]

def format_path(path):
    filepath = ""
    for i in range(len(path)):
        if path[i] != '/':
            filepath += path[i]
        else:
            filepath += '\\'
    return filepath


def execute(path, argv=None):
    if argv is None:
        argv = []
    arr = [path]
    for item in argv:
        arr.append(item)
    subprocess.run(arr)



def get_OS():
    opsys = platform.system()
    if opsys == "":
        Config.log.w(os.path.basename(__file__), "Empty OS name error")
    return opsys


def get_windows_version():
    try:
        wv = sys.getwindowsversion()
        if hasattr(wv, 'service_pack_major'):  # python >= 2.7
            sp = wv.service_pack_major or 0
        else:
            import re
            r = re.search("\s\d$", wv.service_pack)
            sp = int(r.group(0)) if r else 0
        for i in range(len(win_ver)):
            if win_ver[i][1][0] == wv.major and win_ver[i][1][1] == wv.minor and win_ver[i][1][2] == sp:
                return i
    except Exception as e:
        Config.log.e(os.path.basename(__file__), "Windows version querry error.", convert_complex_exception(e))
    return -1

