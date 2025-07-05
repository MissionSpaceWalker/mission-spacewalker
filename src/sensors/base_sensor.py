from abc import ABC, abstractmethod


class BaseSensor(ABC):
    """base class for all sensors"""

    def __init__(self, i2c_port="/dev/i2c-1"):
        self.i2c_port = i2c_port
        self._measuring = False

    @abstractmethod
    def start(self):
        """start measurement"""
        pass

    @abstractmethod
    def stop(self):
        """stop measurement"""
        pass

    @abstractmethod
    def read(self):
        """read data from sensor"""
        pass

    @property
    def is_measuring(self):
        return self._measuring
