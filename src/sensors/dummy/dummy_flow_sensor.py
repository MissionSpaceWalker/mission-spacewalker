#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
import threading
from sensors.base_sensor import BaseSensor


class FlowSensor(BaseSensor):
    """dummy flow sensor for testing"""

    def __init__(self, i2c_port="/dev/i2c-1", slave_address=0x08):
        super().__init__(i2c_port)
        self.slave_address = slave_address
        self._connected = False
        self._thread = None
        self._stop_thread = False

        # dummy sensor parameters
        self._base_flow = 25.0
        self._base_temp = 22.0
        self._product_id = "SF06-LF-DUMMY"
        self._serial_number = "D12345678"

        # current readings
        self._current_flow = self._base_flow
        self._current_temp = self._base_temp
        self._current_flags = 0

    def connect(self):
        print("[DummyFlowSensor] Initializing dummy flow sensor")
        time.sleep(0.1)  # simulate connection time
        self._connected = True

    def disconnect(self):
        print("[DummyFlowSensor] Disconnecting dummy flow sensor")
        if self._measuring:
            self.stop()
        self._connected = False

    def start(self):
        """start dummy measurement"""
        if not self._connected:
            raise RuntimeError("sensor not connected")

        print("[DummySlowSensor] Starting dummy flow measurement")
        self._measuring = True
        self._stop_thread = False

        # start background thread to simulate continuous measurement
        self._thread = threading.Thread(target=self._measurement_loop)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """stop dummy measurement"""
        if self._measuring:
            print("[DummyFlowSensor] Stopping dummy flow measurement")
            self._measuring = False
            self._stop_thread = True
            if self._thread:
                self._thread.join(timeout=1.0)

    def read(self):
        """read dummy data"""
        if not self._connected:
            raise RuntimeError("sensor not connected")
        if not self._measuring:
            raise RuntimeError("measurement not started")

        return {
            "flow": self._current_flow,
            "temperature": self._current_temp,
            "flags": self._current_flags,
            "timestamp": time.time(),
        }

    def get_info(self):
        """get dummy sensor info"""
        if not self._connected:
            raise RuntimeError("sensor not connected")

        return {
            "product_id": self._product_id,
            "serial_number": self._serial_number,
            "sensor_type": "sf06-lf-dummy",
        }

    def _measurement_loop(self):
        """background thread that updates dummy readings"""
        while not self._stop_thread:
            # simulate realistic flow variations
            flow_noise = random.uniform(-2.0, 2.0)
            self._current_flow = max(0, self._base_flow + flow_noise)

            # simulate temperature variations
            temp_noise = random.uniform(-0.5, 0.5)
            self._current_temp = self._base_temp + temp_noise

            # occasionally set flags
            if random.random() < 0.05:  # 5% chance
                self._current_flags = random.randint(1, 3)
            else:
                self._current_flags = 0

            time.sleep(0.02)  # 50 Hz update rate

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
