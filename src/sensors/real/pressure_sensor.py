# lps22_sensor.py

from base_sensor import BaseSensor
import board
import busio
from adafruit_lps2x import LPS22


class PressureSensor(BaseSensor):
    def __init__(self, i2c_port="/dev/i2c-1"):
        super().__init__(i2c_port)
        self._i2c = None
        self._sensor = None
        self._connected = False

    def connect(self):
        """Establish I2C connection and initialize sensor instance"""
        if self._connected:
            print("sensor already connected.")
            return

        self._i2c = busio.I2C(board.SCL, board.SDA)
        while not self._i2c.try_lock():
            pass  # wait for I2C bus lock
        self._i2c.unlock()

        self._sensor = LPS22(self._i2c)
        self._connected = True
        print("sensor connected.")

    def disconnect(self):
        """Power down and clean up the sensor"""
        if not self._connected:
            print("sensor not connected.")
            return

        try:
            self.stop()
        except Exception:
            pass

        self._sensor = None
        self._i2c = None
        self._connected = False
        print("sensor disconnected.")

    def start(self):
        """Starts measurement (configures default rate)"""
        if not self._connected:
            raise RuntimeError("sensor not connected. call connect() first.")

        self._sensor.data_rate = self._sensor.data_rate  # trigger a config
        self._measuring = True

    def stop(self):
        """Stops measurement by setting shutdown mode"""
        if not self._connected:
            return

        self._sensor.data_rate = 0  # shutdown mode
        self._measuring = False

    def read(self):
        """Reads current pressure and temperature"""
        if not self._measuring:
            raise RuntimeError("sensor is not measuring. call ctart() first.")
        if not self._connected:
            raise RuntimeError("sensor not connected. call connect() first.")

        return {
            "pressure_hPa": round(self._sensor.pressure, 2),
            "temperature_C": round(self._sensor.temperature, 2),
        }
