from dataclasses import dataclass
from . import JSONable, Like_Data
from json import dumps as __dumps

@dataclass
class Liked_Data(JSONable):
    object_affected: list
    object_type: str = "liked"

    def __str__(self):
        return f'{self.object_type}, {self.object_affected}'

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'object': self.object_affected
        })