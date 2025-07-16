import time
from sensors.base_sensor import BaseSensor
import random
import threading


class PressureSensor(BaseSensor):
    def __init__(self, i2c_port="/dev/null"):
        super().__init__(i2c_port)

        self._connected = False
        self._thread = None
        self._stop_thread = False

        # dummy sensor parameters
        self._base_pressure = 1013.25  # hPa
        self._base_temp = 25.0  # Celsius
        self._product_id = "DummyPressureSensor"
        self._serial_number = "D12345678"

        # current readings
        self._current_pressure = self._base_pressure
        self._current_temp = self._base_temp

    def start(self):
        if not self._connected:
            raise RuntimeError("Call connect() first.")
        print("[DummyPressureSensor] Starting dummy pressure sensor")
        self._measuring = True
        self._stop_thread = False

        # start background thread to simulate continuous measurement
        self._thread = threading.Thread(target=self._measurement_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        print("[DummyPressureSensor] Stopping dummy pressure sensor")
        if self._measuring:
            self._measuring = False
            self._stop_thread = True
            if self._thread:
                self._thread.join(timeout=1.0)

    def connect(self):
        print("[DummyPressureSensor] Connecting dummy pressure sensor")
        time.sleep(0.1)
        self._connected = True

    def disconnect(self):
        print("[DummyPressureSensor] Disconnecting dummy pressure sensor")
        if self._measuring:
            self.stop()
        self._connected = False

    def read(self):
        """read dummy data"""
        if not self._connected:
            raise RuntimeError("sensor not connected")
        if not self._measuring:
            raise RuntimeError("measurement not started")

        return {
            "pressure_hPa": self._current_pressure,
            "temperature_C": self._current_temp,
        }

    def get_info(self):
        """get sensor info"""
        if not self._connected:
            raise RuntimeError("sensor not connected")

        return {
            "product_id": self._product_id,
            "serial_number": self._serial_number,
            "sensor_type": "dummy_pressure_sensor",
        }

    def _measurement_loop(self):
        """background thread that updates dummy readings"""
        while not self._stop_thread:
            # simulate realistic pressure variations
            pressure_noise = random.uniform(-1.0, 1.0)
            temp_noise = random.uniform(-0.5, 0.5)

            self._current_pressure = round(1013 + pressure_noise, 2)
            self._current_temp = round(25 + temp_noise, 2)

            time.sleep(0.02)  # 50 Hz update rate

    def __enter__(self):
        """context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.disconnect()
