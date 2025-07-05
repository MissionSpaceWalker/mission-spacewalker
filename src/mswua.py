import os
import time

# Conditionally import the dummy or real flow sensor
USE_DUMMY = os.getenv("USE_DUMMY_SENSORS", "false").lower() == "true"

if USE_DUMMY:
    from sensors.dummy_flow_sensor import FlowSensor
else:
    from sensors.flow_sensor import FlowSensor


def main():
    sensors = [
        FlowSensor(),
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
                    print(
                        f"flow: {data['flow']:.2f}; temperature: {data['temperature']:.2f}; flags: {data['flags']};"
                    )
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
