#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

import os
import shutil



"""
File handlers
"""


def writef(name, line):
    try:
        f = open(str(name), "wt", encoding='utf8')
        f.write(str(line))
        f.close()
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/writef/" + str(name) + " --> " + str(line), convert_complex_exception(e), Categories.IO_WRITE_FAILURE)


def appendf(name, line):
    try:
        f = open(str(name), "at", encoding='utf8')
        f.write(str(line))
        f.close()
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/appendf/" + str(name) + " --> " + str(line), convert_complex_exception(e), Categories.IO_APPEND_FAILURE)


def readf(name):
    try:
        arr = []
        sor = []
        f = open(str(name), "rt", encoding='utf8')
        for x in f:
            sor = x.split("\n")
            arr.append(sor[0])
        f.close()
        return arr
    except Exception as e:
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/readf/" + str(name), convert_complex_exception(e), Categories.IO_READ_FAILURE)
        return None


def existf(name):
    try:
        f = open(str(name), "xt", encoding='utf8')
        f.close()
        return False
    except:
        return True


def removef(name):
    try:
        os.remove(str(name))
    except Exception as e:
        pass
        # TODO
        # Config.log.e(os.path.basename(__file__), "IO/removef/" + str(name), convert_complex_exception(e), Categories.IO_REMOVE_FAILURE)


"""
Directory handlers
"""


def getcurrentdir_B():
    try:
        return os.getcwdb()
    except Exception as e:
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/getcurrentdir_B (Byte)", convert_complex_exception(e), Levels.WARNING, Categories.IO_GET_DIR_BYTE_FAILURE)
        return 0


def getcurrentdir_S():
    try:
        return os.getcwd()
    except Exception as e:
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/getcurrentdir_S (String)", convert_complex_exception(e), Categories.IO_GET_DIR_STRING_FAILURE)
        return None


def changedir(name):
    try:
        os.chdir(name)
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/changedir/" + str(name), convert_complex_exception(e), Categories.IO_CHANGE_DIR_FAILURE)


def readdir(name):
    try:
        dirlist = os.scandir(name)
        return dirlist
    except Exception as e:
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/readdir/" + str(name), convert_complex_exception(e), Categories.IO_READ_DIR_FAILURE)
        return None

def existdir(dir_path):
    try:
        return os.path.isdir(dir_path)
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/existdir/" + str(dir_path), convert_complex_exception(e), Categories.IO_EXIST_DIR_FAILURE)

def makedir(name):
    try:
        os.mkdir(name)
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/makedir/" + str(name), convert_complex_exception(e), Categories.IO_MAKE_DIR_FAILURE)


def renamedir(old_name, new_name):
    try:
        os.rename(old_name, new_name)
    except Exception as e:
        pass
        # TODO
        # Config.log.w(os.path.basename(__file__), "IO/renamedir/" + str(old_name) + " --> " + str(new_name), convert_complex_exception(e), Categories.IO_RENAME_DIR_FAILURE)


def removedir(name):
    try:
        shutil.rmtree(name)
    except Exception as e:
        pass
        # TODO
        # Config.log.e(os.path.basename(__file__), "IO/removedir/" + str(name), convert_complex_exception(e), Categories.IO_REMOVE_DIR_FAILURE)

def discover_dir(directory):
    files = []
    for item in os.listdir(directory):
        if os.path.isdir(directory + "\\" +item):
            for file in discover_dir(directory + "\\" +item):
                files.append(file)
        if os.path.isfile(directory + "\\" +item):
            files.append(directory + "\\" +item)
    return files

def only_files_from_dir(directory):
    files=[]
    for item in os.listdir(directory):
        if os.path.isfile(directory + item):
            files.append(directory + item)
    return files