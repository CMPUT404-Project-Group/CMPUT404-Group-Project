from . import JSONable, User_Data
from json import dumps as __dumps

class Like_Data(JSONable):
    def __init__(
            self, context: str, summary: str, object_type: str, 
            author: User_Data, object_affected: str):
        self.context = context
        self.summary = summary
        self.object_type = 'Like'
        self.author = author.get_object_as_JSON()
        self.object_affected = object_affected
    
    def get_object_as_JSON(self):
        return __dumps({
            '@context': self.context,
            'summary': self.summary,
            'type': self.object_type,
            'author': self.author,
            'object': self.object_affected
        })
