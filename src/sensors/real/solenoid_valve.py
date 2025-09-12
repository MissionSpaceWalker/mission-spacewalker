import RPi.GPIO as GPIO
import time

class SolenoidValve:
    def __init__(self, pin=6):  # BCM6 = physical pin 31
        self.pin = pin
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup(self.pin)  # free pin if already in use
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)  # HIGH = OFF (active-LOW)

    def open(self, seconds=None):
        print("Solenoid valve OPEN")
        GPIO.output(self.pin, GPIO.LOW)  # ON
        if seconds:
            time.sleep(seconds)
            self.close()

    def close(self):
        print("Solenoid valve CLOSED")
        GPIO.output(self.pin, GPIO.HIGH)  # OFF

    def auto_close(self, delay=80):
        """Close automatically after delay seconds (non-blocking)."""
        import threading
        threading.Timer(delay, self.close).start()

    def cleanup(self):
        GPIO.cleanup(self.pin)
