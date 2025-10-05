import RPi.GPIO as GPIO
from time import sleep

PIN = 6  # BCM numbering (phys pin 31)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.HIGH)  # start OFF on active-LOW boards

print("Relay ON")
GPIO.output(PIN, GPIO.LOW)   # pull IN low -> relay ON
sleep(2)

print("Relay OFF")
GPIO.output(PIN, GPIO.HIGH)  # release -> relay OFF
GPIO.cleanup()
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setup(6, GPIO.OUT)

print("Valve ON")
GPIO.output(6, GPIO.HIGH)   # energize
sleep(10)                    # keep it on for 10 seconds

print("Valve OFF")
GPIO.output(6, GPIO.LOW)    # turn off
GPIO.cleanup()
