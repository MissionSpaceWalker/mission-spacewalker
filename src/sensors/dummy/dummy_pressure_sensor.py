from sensors.base_sensor import BaseSensor
import random


class PressureSensor(BaseSensor):
    def __init__(self, i2c_port="/dev/null"):
        super().__init__(i2c_port)

    def start(self):
        print("[DummySensor] Starting dummy pressure sensor")
        self._measuring = True

    def stop(self):
        print("[DummySensor] Stopping dummy pressure sensor")
        self._measuring = False

    def connect(self):
        print("[DummySensor] Connecting dummy pressure sensor")
        self._connected = True

    def disconnect(self):
        print("[DummySensor] Disconnecting dummy pressure sensor")
        if self._measuring:
            self.stop()
        self._connected = False

    def read(self):
        if not self._measuring:
            raise RuntimeError("Sensor is not measuring. Call start() first.")

        # Return fake but plausible pressure and temperature values
        return {
            "pressure_hPa": round(random.uniform(980, 1050), 2),
            "temperature_C": round(random.uniform(20, 30), 2),
        }
