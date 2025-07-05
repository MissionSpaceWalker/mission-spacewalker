# adxl335_sensor.py

from sensors.base_sensor import BaseSensor
import analogio
import board


class Accelerometer(BaseSensor):
    def __init__(self, i2c_port="/dev/null"):
        super().__init__(i2c_port)
        self._x = None
        self._y = None
        self._z = None
        self._connected = False

    def connect(self):
        self._x = analogio.AnalogIn(board.A1)
        self._y = analogio.AnalogIn(board.A2)
        self._z = analogio.AnalogIn(board.A3)
        self._connected = True
        print("Accelerometer connected.")

    def disconnect(self):
        self._x.deinit()
        self._y.deinit()
        self._z.deinit()
        self._connected = False
        print("Accelerometer disconnected.")

    def start(self):
        self._measuring = True

    def stop(self):
        self._measuring = False

    def read(self):
        if not self._measuring or not self._connected:
            raise RuntimeError("Sensor not ready.")

        def to_g(axis):
            val = axis.value / 65535.0
            val -= 0.5
            return round(val * 16.0, 2)

        return {
            "x_g": to_g(self._x),
            "y_g": to_g(self._y),
            "z_g": to_g(self._z),
        }
