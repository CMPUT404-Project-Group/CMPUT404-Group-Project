from dataclasses import dataclass
from . import JSONable, User_Data
from json import dumps as __dumps

@dataclass
class User_Request_Data(JSONable):
    object_type: str
    summary: str
    actor: User_Data
    object_affected: User_Data

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'summary': self.summary,
            'actor': self.actor.get_object_as_JSON(),
            'object': self.object_affected.get_object_as_JSON()
        })