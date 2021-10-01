from . import JSONable, Like_Data
from json import dumps as __dumps

class Liked_Data(JSONable):
    def __init__(self, like_data: list):
        self.object_type = "liked"
        self.object_affected = like_data
    
    def get_object_as_JSON(self):
        return __dumps({
            'type': self.object_type,
            'object': self.object_affected
        })