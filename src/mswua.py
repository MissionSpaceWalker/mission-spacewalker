import os
import time

# Conditionally import the dummy or real flow sensor
USE_DUMMY = os.getenv("USE_DUMMY_SENSORS", "false").lower() == "true"

if USE_DUMMY:
    from sensors.dummy.dummy_flow_sensor import FlowSensor
    from sensors.dummy.dummy_pressure_sensor import PressureSensor
    from sensors.dummy.dummy_accelerometer import Accelerometer
else:
    from sensors.real.flow_sensor import FlowSensor
    from sensors.real.pressure_sensor import PressureSensor
    from sensors.real.accelerometer import Accelerometer


def main():
    sensors = [
        FlowSensor(),
        PressureSensor(),
        Accelerometer(),
    ]

    try:
        print("starting all sensors...")
        for sensor in sensors:
            sensor.connect()
            sensor.start()

        print("all sensors started successfully.")
        while True:
            for sensor in sensors:
                try:
                    data = sensor.read()
                    # print the sensor class name, and whatever data it returns
                    sensor_name = sensor.__class__.__name__
                    print(f"{sensor_name} data: {data}")
                except Exception as e:
                    print(f"error reading sensor: {e}")

            time.sleep(0.5)  # read every 0.5 seconds

    except KeyboardInterrupt:
        print("stopping all sensors...")
        for sensor in sensors:
            sensor.stop()
            sensor.disconnect()
        print("all sensors stopped.")


if __name__ == "__main__":
    main()
