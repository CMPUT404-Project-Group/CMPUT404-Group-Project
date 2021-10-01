from typing import Counter
from . import JSONable, User_Data
from json import dumps as __dumps
from datetime import datetime

class Post_Data(JSONable):
    """
    This class is already bloated and I haven't even finished. I don't know how it
    could be improved at the moment.
    """
    def __init__(
            self, title: str, id: str, source: str, origin: str,
            description: str, content_type: str, author: User_Data,
            categories: list, comment_count: int, page_size: int,
            comment_page: str, comments: list, published: datetime,
            visibility: enumerate, unlisted: bool):
        self.object_type = 'post'
        self.title = title
        self.id = id
        self.source = source
        self.origin = origin
        self.description = description
        self.content_type = content_type
        self.author = author
        self.categories = categories
        self.comment_count = comment_count
        self.page_size = page_size
        self.comment_page = comment_page
        self.comments = comments
        self.published = published
        self.visibility = visibility
        self.unlisted = unlisted


    def get_object_as_JSON(self):
        pass