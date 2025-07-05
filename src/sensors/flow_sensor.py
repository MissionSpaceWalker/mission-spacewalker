#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import time

from sensirion_driver_adapters.i2c_adapter.i2c_channel import I2cChannel
from sensirion_i2c_driver import CrcCalculator, I2cConnection, LinuxI2cTransceiver
from sensirion_i2c_sf06_lf.commands import InvFlowScaleFactors
from sensirion_i2c_sf06_lf.device import Sf06LfDevice

from base_sensor import BaseSensor


class FlowSensor(BaseSensor):
    """sf06-lf flow sensor"""

    def __init__(self, i2c_port="/dev/i2c-1", slave_address=0x08):
        super().__init__(i2c_port)
        self.slave_address = slave_address
        self._transceiver = None
        self._channel = None
        self._device = None

    def connect(self):
        """connect to sensor"""
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
            except BaseException:
                pass

    def disconnect(self):
        """disconnect from sensor"""
        if self._measuring:
            self.stop()
        if self._transceiver:
            self._transceiver.__exit__(None, None, None)
            self._transceiver = None
            self._channel = None
            self._device = None

    def start(self):
        """start measurement"""
        if not self._device:
            raise RuntimeError("sensor not connected")
        self._device.start_h2o_continuous_measurement()
        self._measuring = True

    def stop(self):
        """stop measurement"""
        if self._device and self._measuring:
            self._device.stop_continuous_measurement()
            self._measuring = False

    def read(self):
        """read data from sensor"""
        if not self._device:
            raise RuntimeError("sensor not connected")
        if not self._measuring:
            raise RuntimeError("measurement not started")

        flow, temperature, flags = self._device.read_measurement_data(
            InvFlowScaleFactors.SLF3S_0600F
        )
        return {
            "flow": flow,
            "temperature": temperature,
            "flags": flags,
            "timestamp": time.time(),
        }

    def get_info(self):
        """get sensor info"""
        if not self._device:
            raise RuntimeError("sensor not connected")
        product_id, serial_num = self._device.read_product_identifier()
        return {
            "product_id": product_id,
            "serial_number": serial_num,
            "sensor_type": "sf06-lf",
        }

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--i2c-port", "-p", default="/dev/i2c-1")
    parser.add_argument("--samples", "-n", type=int, default=500)
    args = parser.parse_args()

    sensor = FlowSensor(args.i2c_port)

    with sensor:
        # get sensor info
        info = sensor.get_info()
        print(
            f"product_id: {info['product_id']}; serial_number: {info['serial_number']};"
        )

        # start measurement
        sensor.start()

        # collect data
        for i in range(args.samples):
            try:
                time.sleep(0.02)
                data = sensor.read()
                print(
                    f"flow: {data['flow']}; temperature: {data['temperature']}; flags: {data['flags']};"
                )
            except BaseException:
                continue


if __name__ == "__main__":
    main()
