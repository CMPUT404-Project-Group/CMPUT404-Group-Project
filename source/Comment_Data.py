from dataclasses import dataclass, field
from . import JSONable, User_Data
from json import dumps as __dumps
from datetime import datetime

@dataclass(order=True)
class Comment_Data(JSONable):
    """
    Comment_Data is a dataclass which inherits from abstract base class
    JSONable. It represents all of the data necessary to convert
    a given comment from the database into a json object.
    """
    sort_index: datetime = field(init=False, repr=False)
    author: User_Data
    comment: str
    content_type: str
    published: datetime
    id: str
    object_type: str = "comment"

    def __post_init__(self):    
        self.sort_index = self.published
    
    def __str__(self):
        return f'{self.object_type}, {self.id}, {self.published}, {self.author}, {self.comment}'

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.content_type,
            'author': self.author.get_object_as_JSON(),
            'comment': self.comment,
            'contentType': self.content_type,
            'published': self.published,
            'id': self.id
        })