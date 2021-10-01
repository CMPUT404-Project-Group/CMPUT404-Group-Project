from dataclasses import dataclass
from . import JSONable, User_Data
from json import dumps as __dumps

@dataclass
class User_Request_Data(JSONable):
    """
    User_Request_Data is a dataclass which inherits from abstract base class
    JSONable. It represents all of the data necessary to convert
    a given user request data object from the database into a json object.
    """
    object_type: str
    summary: str
    actor: User_Data
    object_affected: User_Data

    def __str__(self):
        return f'{self.object_type}, {self.summary}, {self.actor}, {self.object_affected}'

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'summary': self.summary,
            'actor': self.actor.get_object_as_JSON(),
            'object': self.object_affected.get_object_as_JSON()
        })