from sensors.real.lps22_sensor import PressureSensor
import time

# create sensor instance
sensor = PressureSensor()

# connect to sensor
sensor.connect()

# start measurements
sensor.start()

try:
    while True:
        data = sensor.read()
        print(f"Pressure: {data['pressure_psi']} psi, Temperature: {data['temperature_c']} °C")
        time.sleep(1)  # read every 1 second
except KeyboardInterrupt:
    print("Stopping...")
finally:
    sensor.stop()
    sensor.disconnect()

