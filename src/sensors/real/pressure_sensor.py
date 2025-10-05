# lps22_sensor.py
# lps22_sensor.py

from sensors.base_sensor import BaseSensor, SensorType
import board
import adafruit_lps2x


class PressureSensor(BaseSensor):
    def __init__(self, i2c_port="/dev/i2c-1", address=0x5D):
        super().__init__(sensor_type=SensorType.I2C, i2c_port=i2c_port)
        self._i2c = None
        self._sensor = None
        self._connected = False
        self._address = address  # store which address to use

    def connect(self):
        """establish i2c connection and initialize sensor"""
        if self._connected:
            print(f"LPS22 pressure sensor already connected at 0x{self._address:X}")
            return

        self._i2c = board.I2C()

        # create LPS22 sensor instance at chosen address
        self._sensor = adafruit_lps2x.LPS22(self._i2c, address=self._address)
        self._connected = True
        print(f"LPS22 pressure sensor connected at 0x{self._address:X}")

    def disconnect(self):
        """disconnect and cleanup sensor resources"""
        if not self._connected:
            return

        if self._measuring:
            self.stop()

        self._sensor = None
        self._i2c = None
        self._connected = False
        print(f"LPS22 pressure sensor disconnected at 0x{self._address:X}")

    def start(self):
        """start pressure measurement"""
        if not self._connected:
            raise RuntimeError("sensor not connected - call connect() first")
        self._measuring = True

    def stop(self):
        """stop pressure measurement"""
        if self._connected and self._measuring:
            self._measuring = False

    def read(self):
        """read pressure and temperature data"""
        if not self._connected:
            raise RuntimeError("sensor not connected - call connect() first")
        if not self._measuring:
            raise RuntimeError("sensor not measuring - call start() first")

        pressure_hpa = round(self._sensor.pressure, 2)
        temperature_c = round(self._sensor.temperature, 2)
    
        # convert hPa → psi
        pressure_psi = round(pressure_hpa * 0.0145038, 2)

        return {
            "pressure_psi": pressure_psi,
            "temperature_c": temperature_c,
        }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

