#  Copyright (c) Benedek Szanyó 2023. All rights reserved.

__author__ = "Benedek Szanyó"
__version__ = "0.0.1.14 "
__status__ = "Production"
__date__ = "2023.05.11"
__license__ = "MIT"

import json
from abc import ABC, abstractmethod

from equipments.io.IO import existf


class JSONContainer(ABC):
    def __init__(self):
        self._file_location = None
        pass

    def save(self):
        try:
            with open(self._file_location, "w") as f:
                json.dump(self.toDict(), f)
        except json.JSONDecodeError as e:
            pass

    def _load(self):
        if existf(self._file_location):
            json_str = None
            try:
                with open(self._file_location) as f:
                    json_str = json.load(f)
            except json.JSONDecodeError as e:
                # Config.log.w(class_path, f"Error in JSON file {indicators_file_name}", convert_complex_exception(e))
               pass
            if json_str is not None:
                self.fromDict(json_str)

    @abstractmethod
    def fromDict(self, dict):
        pass

    @abstractmethod
    def toDict(self):
        pass
