from . import JSONable, User_Data
from json import dumps as __dumps

class User_Request_Data(JSONable):

    def __init__(self, type: str, summary: str, actor: User_Data, object_affected: User_Data):
        self.object_type = type
        self.summary = summary
        self.actor = actor.get_object_as_JSON()
        self.object = object_affected.get_object_as_JSON()
    
    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'summary': self.summary,
            'actor': self.actor,
            'object': self.object_affected
        })