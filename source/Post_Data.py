from dataclasses import dataclass, field
from . import JSONable, User_Data
from json import dumps as __dumps
from datetime import datetime

@dataclass
class Post_Data(JSONable):
    sort_index: datetime = field(init=False, repr=False)
    title: str
    id: str
    source: str
    origin: str
    description: str
    content_type: str
    content: str
    author: User_Data
    categories: list
    comment_count: int
    page_size: int
    comment_page: str
    comments: list
    published: datetime
    visibility: enumerate
    unlisted: bool
    object_type: str = 'post'

    def __post_init__(self):
        self.sort_index = self.published
    
    def __str__(self):
        return f'{self.object_type}, {self.id}, {self.published}, {self.author}, {self.content}'

    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'title': self.title,
            'id': self.id,
            'source': self.source,
            'origin': self.origin,
            'description': self.description,
            'contentType': self.content_type,
            'content': self.content,
            'author': self.author.get_object_as_JSON(),
            'categories': self.categories,
            'count': self.comment_count,
            'size': self.page_size,
            'comments': self.comment_page,
            'comments': self.comments,
            'published': self.published,
            'visibility': self.visibility,
            'unlisted': self.unlisted
        })