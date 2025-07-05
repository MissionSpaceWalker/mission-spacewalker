from sensors.base_sensor import BaseSensor
import random


class Accelerometer(BaseSensor):
    def __init__(self, i2c_port="/dev/null"):
        super().__init__(i2c_port)
        self._connected = False

    def connect(self):
        self._connected = True
        print("[DummyAccelerometer] Connected.")

    def disconnect(self):
        self._connected = False
        print("[DummyAccelerometer] Disconnected.")

    def start(self):
        if not self._connected:
            raise RuntimeError("Call connect() first.")
        print("[DummyAccelerometer] Started.")
        self._measuring = True

    def stop(self):
        print("[DummyAccelerometer] Stopped.")
        self._measuring = False

    def read(self):
        if not self._measuring:
            raise RuntimeError("Sensor is not measuring.")
        if not self._connected:
            raise RuntimeError("Sensor not connected.")

        # simulate random small tilts or movements
        return {
            "x_g": round(random.uniform(-1.0, 1.0), 2),
            "y_g": round(random.uniform(-1.0, 1.0), 2),
            "z_g": round(random.uniform(0.0, 1.2), 2),  # gravity range
        }
