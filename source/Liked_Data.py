from dataclasses import dataclass
from . import JSONable, Like_Data
from json import dumps as __dumps

@dataclass
class Liked_Data(JSONable):
    object_affected: list
    object_type: str = "liked"

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'object': self.object_affected
        })