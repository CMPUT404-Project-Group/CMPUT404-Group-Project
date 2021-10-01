from dataclasses import dataclass
from . import JSONable
from json import dumps as __dumps

@dataclass
class User_Data(JSONable):
    id: str
    url: str
    host: str
    display_name: str
    object_type: str = 'author'
    
    def get_object_as_JSON(self):
        return __dumps({
                "type": self.object_type,
                'id': self.id,
                'host': self.host,
                'displayName': self.display_name,
                'url': self.url,
        })