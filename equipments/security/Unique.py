#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

import threading
import time
import uuid
from threading import Thread


class Unique:
    _lock = threading.Lock()
    _instance_num = 0

    def __init__(self, prev_uuid=None):
        self._time = time.time()
        self.uuid = None

        if prev_uuid is not None:
            self.uuid = prev_uuid

    def generate_uuid(self):
        with Unique._lock:
            if self.uuid is None:
                self._time = time.time()
                current_time = str(self._time)
                Unique._instance_num += 1
                self.uuid = str(Unique._instance_num) + '_' + str(uuid.uuid4()) + '_' + current_time

    def get_instance_num(self):
        return Unique._instance_num


def task():
    unique = Unique()
    unique.generate_uuid()
    print(unique.uuid)


if __name__ == "__main__":
    threads = [Thread(target=task, args=()) for _ in range(1000)]
    # start threads
    for thread in threads:
        thread.start()
    # wait for threads
    for thread in threads:
        thread.join()
    print("Done")
