# lps22_sensor.py

from sensors.base_sensor import BaseSensor, SensorType
import board
import adafruit_lps2x


class PressureSensor(BaseSensor):
    def __init__(self, i2c_port="/dev/i2c-1"):
        super().__init__(sensor_type=SensorType.I2C, i2c_port=i2c_port)
        self._i2c = None
        self._sensor = None
        self._connected = False

    def connect(self):
        """establish i2c connection and initialize sensor"""
        if self._connected:
            print("lps22 pressure sensor already connected")
            return

        # use board.I2C() instead of busio.I2C()
        self._i2c = board.I2C()

        # create LPS22 sensor instance
        self._sensor = adafruit_lps2x.LPS22(self._i2c)
        self._connected = True
        print("lps22 pressure sensor connected")

    def disconnect(self):
        """disconnect and cleanup sensor resources"""
        if not self._connected:
            return

        if self._measuring:
            self.stop()

        self._sensor = None
        self._i2c = None
        self._connected = False
        print("lps22 pressure sensor disconnected")

    def start(self):
        """start pressure measurement"""
        if not self._connected:
            raise RuntimeError("sensor not connected - call connect() first")

        # no need to configure data rate - sensor is ready to read
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
        """context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.disconnect()
