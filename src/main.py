# from sensors.temperature_sensor import TemperatureSensor
# from sensors.pressure_sensor import PressureSensor


def main():
    # sensors = [
    #     TemperatureSensor(),
    #     PressureSensor(),
    # ]

    try:
        print("Starting all sensors...")
        # for sensor in sensors:
        #     sensor.start()

        while True:
            pass  # Keep alive or add monitoring here

    except KeyboardInterrupt:
        print("Stopping all sensors...")
        # for sensor in sensors:
        #     sensor.stop()


if __name__ == "__main__":
    main()
