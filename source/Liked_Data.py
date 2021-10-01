from dataclasses import dataclass
from . import JSONable, Like_Data
from json import dumps as __dumps

@dataclass
class Liked_Data(JSONable):
    """
    Liked_Data is a dataclass which inherits from abstract base class
    JSONable. It represents all of the data necessary to convert
    a given liked object from the database into a json object.
    """
    object_affected: list
    object_type: str = "liked"

    def __str__(self):
        return f'{self.object_type}, {self.object_affected}'

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'object': self.object_affected
        })