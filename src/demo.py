import time
from contextlib import ExitStack

USE_DUMMY = False

if USE_DUMMY:
    from sensors.dummy.dummy_flow_sensor import FlowSensor
    from sensors.dummy.dummy_pressure_sensor import PressureSensor
else:
    from sensors.real.flow_sensor import FlowSensor
    from sensors.real.pressure_sensor import PressureSensor

def run_sensors():
    with ExitStack() as stack:
        sensors = []
        for sensor_class in [FlowSensor, PressureSensor]:
            sensor = stack.enter_context(sensor_class())
            sensor.start()
            sensors.append(sensor)

        print("Sensors started. Press Ctrl+C to stop.\n")
        while True:
            for sensor in sensors:
                try:
                    data = sensor.read()
                    print(f"{sensor.__class__.__name__}: {data}")
                except Exception as e:
                    print(f"Error reading {sensor.__class__.__name__}: {e}")
            time.sleep(1)  # adjust polling rate here

if __name__ == "__main__":
    run_sensors()
