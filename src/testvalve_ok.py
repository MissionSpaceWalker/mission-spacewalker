# file: testvalve_ok.py
import RPi.GPIO as GPIO, time

PIN = 6  # BCM numbering (physical pin 31)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)              # silence "channel in use" warning
GPIO.cleanup(PIN)                    # free the pin in case a prior run left it busy
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.HIGH)  # HIGH = OFF for active-LOW boards

try:
    print("Relay ON (valve should pop)")
    GPIO.output(PIN, GPIO.LOW)       # pull IN low -> relay ON
    time.sleep(2)

    print("Relay OFF")
    GPIO.output(PIN, GPIO.HIGH)      # release -> relay OFF
    time.sleep(0.5)
finally:
    GPIO.cleanup(PIN)
import RPi.GPIO as GPIO, time
PIN = 6  # BCM (phys 31) or whichever pin you verified with pinout

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.cleanup(PIN)
GPIO.setup(PIN, GPIO.OUT, initial=GPIO.HIGH)  # OFF for active-LOW module

def open_valve(seconds=None):
    GPIO.output(PIN, GPIO.LOW)   # ON
    if seconds:
        time.sleep(seconds)
        close_valve()

def close_valve():
    GPIO.output(PIN, GPIO.HIGH)  # OFF

try:
    open_valve(2)   # open for 2s -> pop
    time.sleep(1)
    close_valve()   # close -> add TVS to get a pop here too
    # or use valve_off_with_click() from section 1 if you just want an audible relay click
finally:
    GPIO.cleanup(PIN)
