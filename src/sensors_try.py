from sensors.real.flow_sensor import FlowSensor
from sensors.real.pressure_sensor import PressureSensor
from contextlib import ExitStack
import time

with ExitStack() as stack:
    flow = stack.enter_context(FlowSensor())
    flow.start()
    
    pressure = stack.enter_context(PressureSensor())
    pressure.start()

    print("Sensors started. Reading values:")
    try:
        while True:
            f_data = flow.read()
            p_data = pressure.read()
            print(f"Flow: {f_data}, Pressure: {p_data}")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping sensors...")
