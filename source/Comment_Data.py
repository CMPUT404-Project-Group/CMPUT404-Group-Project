from . import JSONable, User_Data
from json import dumps as __dumps
from datetime import datetime

class Comment_Data(JSONable):
    def __init__(
            self, author: User_Data, comment: str, content_type: str,
            published: datetime, id: str):
        self.object_type = "comment"
        self.author = author.get_object_as_JSON()
        self.comment = comment
        self.content_type = content_type
        self.published = published
        self.id = id
    
    def get_object_as_JSON(self):
        return __dumps({
            'type': self.content_type,
            'author': self.author,
            'comment': self.comment,
            'contentType': self.content_type,
            'published': self.published,
            'id': self.id
        })