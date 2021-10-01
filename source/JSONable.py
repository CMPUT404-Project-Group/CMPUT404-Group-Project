from dataclasses import dataclass
from abc import ABC, abstractmethod, abstractproperty

@dataclass
class JSONable(ABC):
    """
    Abstract base class to be inheirted by
    any object which requires the ability to become
    JSON
    """
    object_type: str

    @abstractmethod
    def get_object_as_JSON(self):
        """
        Function which should take a given object which is JSONable
        and turn it into a JSON object
        """
        pass