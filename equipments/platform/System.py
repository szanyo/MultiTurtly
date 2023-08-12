#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.10 "
__status__ = "Production"
__date__ = "2023.05.07"
__license__ = "MIT"

import ctypes
import multiprocessing
import os
import platform
import subprocess
from subprocess import Popen, DEVNULL
import sys

import psutil


class AdminStateUnknownError(Exception):
    """Cannot determine whether the user is an admin."""
    pass


class System:
    @staticmethod
    def get_cpu_count():
        return multiprocessing.cpu_count()
        # print(f"Number of CPUs: {num_cpus}")

    @staticmethod
    def get_core_count():
        return psutil.cpu_count(logical=False)
        # print(f"Number of CPU cores: {num_cores}")

    @staticmethod
    def get_thread_count():
        return os.cpu_count()
        # print(f"Number of threads: {num_threads}")

    @staticmethod
    def get_logical_cpu_count():
        return psutil.cpu_count(logical=True)
        # print(f"Number of logical CPUs: {num_logical_cpus}")

    @staticmethod
    def is_user_admin():
        # type: () -> bool
        """Return True if user has admin privileges.

        Raises:
            AdminStateUnknownError if user privileges cannot be determined.
        """
        try:
            return os.getuid() == 0
        except AttributeError:
            pass
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() == 1
        except AttributeError:
            raise AdminStateUnknownError

    @staticmethod
    def get_admin_priv():
        if platform.system().lower() == 'windows':
            import ctypes, sys
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            exit(0)

    @staticmethod
    def path():
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        elif __file__:
            return os.path.dirname(__file__)
        else:
            print("WARNING: No path found")
            return os.getcwd()
