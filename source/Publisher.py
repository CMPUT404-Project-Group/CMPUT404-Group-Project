from abc import ABC, abstractmethod, abstractproperty
class Publisher(ABC):
    @abstractproperty
    def subscribers():
        pass

    @abstractmethod
    def notify_subscribers():
        """
        This function is called when the publisher publishes
        new material, it should iterate through all of it's
        subscribers calling update on them as it goes
        """
        pass