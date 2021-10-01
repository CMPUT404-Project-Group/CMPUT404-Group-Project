from dataclasses import dataclass
from . import JSONable, User_Data
from json import dumps as __dumps

@dataclass
class Like_Data(JSONable):
    """
    Like_Data is a dataclass which inherits from abstract base class
    JSONable. It represents all of the data necessary to convert
    a given like from the database into a json object.
    """
    context: str
    summary: str
    author: User_Data
    object_affected: str
    object_type: str = "Like"

    def __str__(self):
        return f'{self.object_type}, {self.context}, {self.summary}, {self.author}, {self.object_affected}'
    
    def get_object_as_JSON(self):
        return __dumps({
            '@context': self.context,
            'summary': self.summary,
            'type': self.object_type,
            'author': self.author.get_object_as_JSON(),
            'object': self.object_affected
        })
