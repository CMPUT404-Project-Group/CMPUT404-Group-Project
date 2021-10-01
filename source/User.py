from abc import ABC, abstractmethod, abstractproperty

class User(ABC):
    @abstractproperty
    def user_data():
        pass
    
    @abstractmethod
    def get_posts(self):
        pass
