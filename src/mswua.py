import os
import time
from contextlib import ExitStack

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
    sensor_classes = [
        FlowSensor,
        PressureSensor,
        Accelerometer,
    ]

    try:
        print("starting all sensors...")

        # manages multiple context managers
        with ExitStack() as stack:
            # enter all sensor contexts and start them
            sensors = []
            for sensor_class in sensor_classes:
                sensor = stack.enter_context(sensor_class())
                sensor.start()
                sensors.append(sensor)

            print("all sensors started successfully.")

            while True:
                for sensor in sensors:
                    try:
                        data = sensor.read()
                        sensor_name = sensor.__class__.__name__
                        print(f"{sensor_name} data: {data}")
                    except Exception as e:
                        print(f"error reading {sensor.__class__.__name__}: {e}")

                time.sleep(0.5)  # read every 0.5 seconds

    except KeyboardInterrupt:
        print("stopping all sensors...")
        # context managers will automatically handle disconnect()
        print("all sensors stopped.")


if __name__ == "__main__":
    main()
