from abc import ABC, abstractmethod
from enum import Enum


class SensorType(Enum):
    """enumeration for different sensor communication types"""

    I2C = "i2c"
    ANALOG = "analog"
    SPI = "spi"  # for future expansion


class BaseSensor(ABC):
    """base class for all sensors - supports i2c, analog, and other communication types"""

    def __init__(self, sensor_type=SensorType.I2C, i2c_port="/dev/i2c-1", **kwargs):
        """
        initialize base sensor

        args:
            sensor_type: type of sensor communication (i2c, analog, etc.)
            i2c_port: i2c device path for i2c sensors
            **kwargs: additional sensor-specific parameters (supply_voltage, etc.)
        """
        self.sensor_type = sensor_type
        self.i2c_port = i2c_port if sensor_type == SensorType.I2C else None
        self._measuring = False

        # store any additional parameters for sensor-specific use
        self.sensor_params = kwargs

    @abstractmethod
    def connect(self):
        """establish connection to sensor hardware"""
        pass

    @abstractmethod
    def disconnect(self):
        """disconnect from sensor hardware and cleanup resources"""
        pass

    @abstractmethod
    def start(self):
        """start measurement process"""
        pass

    @abstractmethod
    def stop(self):
        """stop measurement process"""
        pass

    @abstractmethod
    def read(self):
        """read data from sensor - returns dict with sensor readings"""
        pass

    @property
    def is_measuring(self):
        """check if sensor is currently measuring"""
        return self._measuring

    @property
    def is_i2c_sensor(self):
        """check if this is an i2c sensor"""
        return self.sensor_type == SensorType.I2C

    @property
    def is_analog_sensor(self):
        """check if this is an analog sensor"""
        return self.sensor_type == SensorType.ANALOG
