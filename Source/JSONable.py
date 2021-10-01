from abc import ABC, abstractmethod, abstractproperty

class JSONable(ABC):
    """
    Abstract base class to be inheirted by
    any object which requires the ability to become
    JSON
    """
    @abstractproperty
    def object_type():
        pass

    @abstractmethod
    def get_object_as_JSON():
        pass