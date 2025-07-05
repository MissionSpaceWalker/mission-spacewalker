import threading
import time
from sensors.base_sensor import BaseSensor
import random


class Accelerometer(BaseSensor):
    def __init__(self, i2c_port="/dev/null"):
        super().__init__(i2c_port)
        self._connected = False
        self._thread = None
        self._stop_thread = False

        # dummy sensor parameters
        self._product_id = "DummyAccelerometer"
        self._serial_number = "D12345678"

        # current readings
        self._current_readings = {
            "x_g": 0.0,
            "y_g": 0.0,
            "z_g": 1.0,  # assuming z-axis is aligned with gravity
        }

    def connect(self):
        print("[DummyAccelerometer] Connecting to dummy accelerometer...")
        time.sleep(0.1)  # simulate connection time
        self._connected = True

    def disconnect(self):
        print("[DummyAccelerometer] Disconnecting dummy accelerometer...")
        if self._measuring:
            self.stop()
        self._connected = False

    def start(self):
        if not self._connected:
            raise RuntimeError("sensor not connected")
        print("[DummyAccelerometer] Starting dummy accelerometer measurement.")
        self._measuring = True
        self._stop_thread = False

        # start background thread to simulate continuous measurement
        self._thread = threading.Thread(target=self._measurement_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        print("[DummyAccelerometer] Stopping dummy accelerometer measurement.")
        if self._measuring:
            self._measuring = False
            self._stop_thread = True
            if self._thread:
                self._thread.join(timeout=1.0)

    def read(self):
        if not self._measuring:
            raise RuntimeError("Sensor is not measuring.")
        if not self._connected:
            raise RuntimeError("Sensor not connected.")

        return {
            "x_g": self._current_readings["x_g"],
            "y_g": self._current_readings["y_g"],
            "z_g": self._current_readings["z_g"],
        }

    def get_info(self):
        """get dummy accelerometer info"""
        return {
            "product_id": self._product_id,
            "serial_number": self._serial_number,
            "sensor_type": "dummy-accelerometer",
        }

    def _measurement_loop(self):
        """background thread that updates dummy readings"""
        while not self._stop_thread:
            # simulate realistic accelerometer variations
            x_noise = random.uniform(-0.1, 0.1)
            y_noise = random.uniform(-0.1, 0.1)
            z_noise = random.uniform(-0.05, 0.05)

            # update current readings
            self._current_readings = {
                "x_g": round(self._current_readings["x_g"] + x_noise, 2),
                "y_g": round(self._current_readings["y_g"] + y_noise, 2),
                "z_g": round(self._current_readings["z_g"] + z_noise, 2),
            }

            time.sleep(0.02)  # 50 Hz update rate

    def __enter__(self):
        """context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.disconnect()
