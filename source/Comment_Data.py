from dataclasses import dataclass
from . import JSONable, User_Data
from json import dumps as __dumps
from datetime import datetime

@dataclass
class Comment_Data(JSONable):
    author: User_Data
    comment: str
    content_type: str
    published: datetime
    id: str
    object_type: str = "comment"
    

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.content_type,
            'author': self.author.get_object_as_JSON(),
            'comment': self.comment,
            'contentType': self.content_type,
            'published': self.published,
            'id': self.id
        })