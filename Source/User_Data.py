from . import JSONable
from json import dumps as __dumps

class User_Data(JSONable):

    def __init__(self, id: str, url: str, host: str, display_name: str):
        self.object_type = "author"
        self.id = id
        self.url = url
        self.host = host
        self.display_name = display_name
    
    def get_object_as_JSON(self):
        return __dumps({
                "type": self.object_type,
                'id': self.id,
                'host': self.host,
                'displayName': self.display_name,
                'url': self.url,
        })