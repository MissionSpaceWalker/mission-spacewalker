import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)

GPIO.output(21, 0)  # ON
sleep(5)
GPIO.output(21, 1)  # OFF
