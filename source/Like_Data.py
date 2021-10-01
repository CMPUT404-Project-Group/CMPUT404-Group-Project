from dataclasses import dataclass
from . import JSONable, User_Data
from json import dumps as __dumps

@dataclass
class Like_Data(JSONable):
    context: str
    summary: str
    author: User_Data
    object_affected: str
    object_type: str = "Like"
    
    def get_object_as_JSON(self):
        return __dumps({
            '@context': self.context,
            'summary': self.summary,
            'type': self.object_type,
            'author': self.author.get_object_as_JSON(),
            'object': self.object_affected
        })
