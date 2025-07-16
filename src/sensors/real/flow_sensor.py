#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time
import logging

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_driver import CrcCalculator, I2cConnection, LinuxI2cTransceiver
from sensirion_i2c_sf06_lf.commands import InvFlowScaleFactors
from sensirion_i2c_sf06_lf.device import Sf06LfDevice

from base_sensor import BaseSensor, SensorType


class FlowSensor(BaseSensor):
    """slf3s-0600f liquid flow sensor"""

    def __init__(self, i2c_port="/dev/i2c-1", slave_address=0x08):
        """
        initialize slf3s-0600f flow sensor

        args:
            i2c_port: i2c device path
            slave_address: i2c slave address (default 0x08)
        """
        super().__init__(sensor_type=SensorType.I2C, i2c_port=i2c_port)
        self.slave_address = slave_address
        self._transceiver = None
        self._channel = None
        self._device = None
        self._connected = False

        # scale factor for slf3s-0600f
        self.scale_factor = InvFlowScaleFactors.SLF3S_0600F

    def connect(self):
        """connect to sensor and initialize i2c communication"""
        try:
            if self._transceiver is None:
                self._transceiver = LinuxI2cTransceiver(self.i2c_port)
                self._transceiver.__enter__()
                self._channel = I2cChannel(
                    I2cConnection(self._transceiver),
                    slave_address=self.slave_address,
                    crc=CrcCalculator(8, 0x31, 0xFF, 0x0),
                )
                self._device = Sf06LfDevice(self._channel)

                # try to stop any running measurement
                try:
                    self._device.stop_continuous_measurement()
                    time.sleep(0.1)
                except Exception as e:
                    logging.warning(f"could not stop existing measurement: {e}")

                self._connected = True
                print("slf3s-0600f flow sensor connected")

        except Exception as e:
            self._cleanup()
            raise RuntimeError(f"failed to connect to flow sensor: {e}")

    def disconnect(self):
        """disconnect from sensor and cleanup resources"""
        if self._measuring:
            self.stop()
        self._cleanup()
        print("slf3s-0600f flow sensor disconnected")

    def _cleanup(self):
        """internal cleanup method"""
        if self._transceiver:
            try:
                self._transceiver.__exit__(None, None, None)
            except Exception:
                pass
            self._transceiver = None
            self._channel = None
            self._device = None
            self._connected = False

    def start(self):
        """start continuous flow measurement"""
        if not self._connected or not self._device:
            raise RuntimeError("sensor not connected - call connect() first")

        try:
            self._device.start_h2o_continuous_measurement()
            self._measuring = True
            print("flow measurement started")
        except Exception as e:
            raise RuntimeError(f"failed to start measurement: {e}")

    def stop(self):
        """stop continuous flow measurement"""
        if self._device and self._measuring:
            try:
                self._device.stop_continuous_measurement()
                self._measuring = False
                print("flow measurement stopped")
            except Exception as e:
                logging.warning(f"error stopping measurement: {e}")

    def read(self):
        """read flow data from sensor"""
        if not self._connected or not self._device:
            raise RuntimeError("sensor not connected")
        if not self._measuring:
            raise RuntimeError("measurement not started - call start() first")

        try:
            flow, temperature, flags = self._device.read_measurement_data(
                self.scale_factor
            )
            return {
                "flow_ml_min": flow,  # more descriptive name
                "temperature_c": temperature,
                "flags": flags,
                "timestamp": time.time(),
            }
        except Exception as e:
            raise RuntimeError(f"failed to read sensor data: {e}")

    def get_info(self):
        """get sensor product information"""
        if not self._connected or not self._device:
            raise RuntimeError("sensor not connected")

        try:
            product_id, serial_num = self._device.read_product_identifier()
            return {
                "product_id": product_id,
                "serial_number": serial_num,
                "sensor_type": "slf3s-0600f",
                "i2c_address": hex(self.slave_address),
            }
        except Exception as e:
            raise RuntimeError(f"failed to read sensor info: {e}")

    def __enter__(self):
        """context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """context manager exit"""
        self.disconnect()
