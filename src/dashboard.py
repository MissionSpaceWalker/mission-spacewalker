import tkinter as tk
from tkinter import ttk
import random
import time
from contextlib import ExitStack
import threading
from stepper_motor import StepperMotor

USE_DUMMY = False

if USE_DUMMY:
    from sensors.dummy.dummy_flow_sensor import FlowSensor
    from sensors.dummy.dummy_pressure_sensor import PressureSensor
   # from sensors.dummy.dummy_accelerometer import Accelerometer
else:
    from sensors.real.flow_sensor import FlowSensor
    from sensors.real.pressure_sensor import PressureSensor
    # from sensors.real.accelerometer import Accelerometer


class MissionSpacewalkerDashboard(tk.Tk):
    def __init__(self, mode="dummy"):
        super().__init__()
        self.title("Mission SpaceWalker - Bioreactor Dashboard")
        self.geometry("1400x800")
        self.mode = mode

        self.sensor_classes = [
            FlowSensor,
            PressureSensor,
            # Accelerometer,
        ]

        # basic system state
        self.running = False
        self.pressure_threshold = 105.0

        # store recent flow values for graph
        self.flow_data = []
        self.max_points = 100   # max number of data points to keep
        self.update_interval_ms = 1000  # sensor update frequency in ms

        # Initialize motor
        self.motor = StepperMotor()
        
        self._create_widgets()
        

    # build the ui layout
    def _create_widgets(self):
        # top frame will hold both camera feeds side by side and controls
        top_frame = tk.Frame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        # cameras frame for the two camera feeds
        cameras_frame = tk.Frame(top_frame)
        cameras_frame.pack(side="left")

        # controls frame in top right corner
        controls_frame = tk.Frame(top_frame)
        controls_frame.pack(side="right", anchor="n", padx=(20, 0))

        # bottom frame will hold sensor readings
        bottom_frame = tk.Frame(self, bg="#1c1c1c")
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # camera 1 placeholder - side by side layout
        self.cam1_group = ttk.LabelFrame(cameras_frame, text="Camera Feed 1")
        self.cam1_group.pack(side="left", padx=(0, 5))
        self.cam1_canvas = tk.Canvas(
            self.cam1_group, width=560, height=420, bg="black", highlightthickness=0)
        self.cam1_canvas.pack()
        self._draw_camera_placeholder(self.cam1_canvas, "no feed")

        # camera 2 placeholder - side by side layout
        self.cam2_group = ttk.LabelFrame(cameras_frame, text="Camera Feed 2")
        self.cam2_group.pack(side="left", padx=(5, 0))
        self.cam2_canvas = tk.Canvas(
            self.cam2_group, width=560, height=420, bg="black", highlightthickness=0)
        self.cam2_canvas.pack()
        self._draw_camera_placeholder(self.cam2_canvas, "no feed")

        # start/stop controls in top right corner
        self.start_button = tk.Button(
            controls_frame, text="START", command=self.start_system,
            font=("Arial", 14), width=15, height=2)
        self.start_button.pack(pady=(0, 10))

        self.stop_button = tk.Button(
            controls_frame, text="EMERGENCY STOP", bg="white",
            fg="red",
            font=("Arial", 14, "bold"),
            width=20, height=2,
            command=self.stop_system
        )
        self.stop_button.pack()

        # sensor readings section - larger fonts and spacing
        sensor_frame = tk.Frame(bottom_frame, bg="#1c1c1c")
        sensor_frame.pack(fill="x", pady=(20, 0))

        self.pressure_label = tk.Label(sensor_frame, text="Pressure: --- kPa",
                                       fg="white", bg="#1c1c1c", font=("Arial", 18, "bold"))
        self.pressure_label.pack(anchor="w", pady=10)

        self.flow_label = tk.Label(sensor_frame, text="Flow Rate: --- mL/min",
                                   fg="white", bg="#1c1c1c", font=("Arial", 18, "bold"))
        self.flow_label.pack(anchor="w", pady=10)

        self.temp_label = tk.Label(sensor_frame, text="Temperature: --- °C",
                                   fg="white", bg="#1c1c1c", font=("Arial", 18, "bold"))
        self.temp_label.pack(anchor="w", pady=10)

    # draw a placeholder box with a message for the camera feeds
    def _draw_camera_placeholder(self, canvas: tk.Canvas, msg: str):
        w = int(canvas["width"])
        h = int(canvas["height"])
        canvas.delete("all")
        canvas.create_rectangle(
            5, 5, w-5, h-5, outline="#2ecc71", width=2)  # Thicker border
        canvas.create_line(10, 10, w-10, h-10, fill="#2ecc71", width=2)
        canvas.create_line(w-10, 10, 10, h-10, fill="#2ecc71", width=2)
        canvas.create_text(w//2, h//2, text=msg,
                           # Larger font
                           fill="#2ecc71", font=("Arial", 14, "bold"))

    def _run_system(self):
        try:
            print("starting all sensors...")

            # manages multiple context managers
            with ExitStack() as stack:
                # enter all sensor contexts and start them
                sensors = []
                for sensor_class in self.sensor_classes:
                    sensor = stack.enter_context(sensor_class())
                    sensor.start()
                    sensors.append(sensor)

                print("all sensors started successfully.")

                while True:
                    flow_value = None
                    pressure_value = None
                    temperature_value = None
                    for sensor in sensors:
                        try:
                            data = sensor.read()
                            sensor_name = sensor.__class__.__name__

                            if sensor_name == "FlowSensor":
                              if isinstance(data,dict) and "flow_µl_min" in data:
                                flow_value = data['flow_µl_min']
                              else:
                                print("garbage <3")
                            if sensor_name == "PressureSensor":
                              pressure_value = data['pressure_psi']
                              temperature_value = data['temperature_c']
                              
                        except Exception as e:
                            print(
                                f"error reading {sensor.__class__.__name__}: {e}")

                    # ! fake sensor data here
                    # TODO: find a way to read real data from above and shove it into the labels
                    self._update_sensors(
                        flow=flow_value,
                        pressure=pressure_value,
                        temp=temperature_value,
                    )
                    time.sleep(0.5)  # read every 0.5 seconds

        except KeyboardInterrupt:
            print("stopping all sensors...")
            # context managers will automatically handle disconnect()
            print("all sensors stopped.")

    # start reading/updating the sensors

    def start_system(self):
        if self.running:
            return
        
        print("System started → opening valve")
        threading.Thread(target=lambda: self.motor.fixed_steps(1500), daemon=True).start()
        self.running = True

        # start thread in background to avoid blocking the UI
        thread = threading.Thread(target=self._run_system)
        thread.daemon = True  # allow exit without waiting for this thread
        thread.start()

        # self._tick()

    # stop the system loop
    def stop_system(self):
        self.running = False
        print("system emergency stop triggered")

        print("Emergency stop → closing valve") 
        threading.Thread(target=lambda: self.motor.fixed_steps(-1500), daemon=True).start()
        self.running = False

    # called every update interval to refresh values
    def _tick(self):
        if not self.running:
            return

        # fake sensor data here
        # replace with real hardware readings later
        flow = random.uniform(0.5, 1.5)
        pressure = random.uniform(90, 115)
        temp = random.uniform(20, 25)

        self._update_sensors(flow, pressure, temp)
        # self._update_graph(flow)
        self._update_cameras_placeholder()

        self.after(self.update_interval_ms, self._tick)

    # update the label text/colors for sensor readings
    def _update_sensors(self, flow: float, pressure: float, temp: float):
        color = "red" if pressure > self.pressure_threshold else "white"
        self.pressure_label.config(
            text=f"Pressure: {pressure} psi", fg=color)
        self.flow_label.config(text=f"Flow Rate: {flow} mL/min")
        self.temp_label.config(text=f"Temperature: {temp} °C")

    # store the new flow value and trigger a redraw
    def _update_graph(self, flow: float):
        self.flow_data.append(flow)
        if len(self.flow_data) > self.max_points:
            self.flow_data = self.flow_data[-self.max_points:]
        self._redraw_graph()

    # redraw the flow graph from stored data
    def _redraw_graph(self):
        c = self.graph_canvas
        c.delete("all")
        w = c.winfo_width()
        h = c.winfo_height()
        if w < 10 or h < 10:
            return

        # more padding on the left for y-axis numbers
        pad_left = 20
        pad_right = 20
        pad_top = 20
        pad_bottom = 30

        x0, y0 = pad_left, pad_top
        x1, y1 = w - pad_right, h - pad_bottom

        # draw main rectangle (plot area)
        c.create_rectangle(x0, y0, x1, y1, outline="#cccccc")

        if not self.flow_data:
            c.create_text(w//2, h//2, text="no data yet", fill="#888")
            return

        data = self.flow_data
        x_step = (x1 - x0) / max(1, self.max_points - 1)
        ymin = min(data) - 0.1
        ymax = max(data) + 0.1
        if abs(ymax - ymin) < 1e-6:
            ymax = ymin + 1.0

        def to_xy(i, val):
            x = x0 + i * x_step
            y = y1 - (val - ymin) / (ymax - ymin) * (y1 - y0)
            return x, y

        # horizontal grid lines + y-axis labels
        for frac in (0.0, 0.25, 0.5, 0.75, 1.0):
            y = y1 - frac * (y1 - y0)
            c.create_line(x0, y, x1, y, fill="#eeeeee")
            val = ymin + frac * (ymax - ymin)
            # align numbers to the left of the y-axis
            c.create_text(
                x0 - 5, y, text=f"{val:.2f}", anchor="e", fill="#666")

        # draw the flow line
        points = []
        for i, val in enumerate(data[-self.max_points:]):
            points.extend(to_xy(i, val))
        if len(points) >= 4:
            c.create_line(points, width=2)

        # axis labels
        c.create_text((x0 + x1)//2, y1 + 18,
                      text="time (samples)", fill="#444")
        c.create_text(x0 - 50, (y0 + y1)//2,
                      text="flow", angle=90, fill="#444")

    # temporary: updates camera placeholders so it looks alive
    def _update_cameras_placeholder(self):
        for canvas in (self.cam1_canvas, self.cam2_canvas):
            self._draw_camera_placeholder(canvas, "no feed")
            r = 8  # Slightly larger indicator
            canvas.create_oval(8, 8, 8 + r, 8 + r, fill="#2ecc71", outline="")


if __name__ == "__main__":
    app = MissionSpacewalkerDashboard()
    app.mainloop()
