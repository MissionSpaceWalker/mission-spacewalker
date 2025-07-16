from sensors.base_sensor import BaseSensor, SensorType
import analogio
import board


class Accelerometer(BaseSensor):
    def __init__(self, supply_voltage=3.3):
        """
        initialize adxl326 analog accelerometer

        args:
            supply_voltage: sensor supply voltage (3.3v or 5v)
        """
        super().__init__(sensor_type=SensorType.ANALOG, supply_voltage=supply_voltage)
        self.supply_voltage = self.sensor_params.get("supply_voltage", 3.3)
        self._x = None
        self._y = None
        self._z = None
        self._connected = False

    def connect(self):
        """connect to analog pins for x, y, z axes"""
        self._x = analogio.AnalogIn(board.A1)
        self._y = analogio.AnalogIn(board.A2)
        self._z = analogio.AnalogIn(board.A3)
        self._connected = True
        print("adxl326 accelerometer connected to analog pins")

    def disconnect(self):
        """disconnect and cleanup analog pin resources"""
        if self._connected:
            self._x.deinit()
            self._y.deinit()
            self._z.deinit()
            self._connected = False
            print("adxl326 accelerometer disconnected")

    def start(self):
        """start measuring acceleration"""
        if not self._connected:
            raise RuntimeError("sensor not connected - call connect() first")
        self._measuring = True

    def stop(self):
        """stop measuring acceleration"""
        self._measuring = False

    def read(self):
        """read acceleration data from all three axes"""
        if not self._measuring or not self._connected:
            raise RuntimeError("sensor not ready - ensure connected and measuring")

        return {
            "x_g": self._convert_to_g(self._x),
            "y_g": self._convert_to_g(self._y),
            "z_g": self._convert_to_g(self._z),
        }

    def _convert_to_g(self, axis):
        """convert analog reading to g-force for adxl326"""
        # convert adc reading to 0...1 range
        val = axis.value / 65535.0
        # shift to center around 0
        val -= 0.5
        # convert to g-force (±16g range for adxl326)
        return round(val * 32.0, 2)

    def __enter__(self):
        """context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.disconnect()
