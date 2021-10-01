from abc import ABC, abstractmethod, abstractproperty

class Subsriber(ABC):
    @abstractmethod
    def update():
        """
        This function should perform all necessary actions in the event that
        the publisher publishes new material
        """
        pass