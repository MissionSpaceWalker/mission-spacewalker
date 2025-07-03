import pigpio
import time

# “BCM” means we address pins by the Broadcom chip numbers, e.g. 18.
# so if the wires come out or we cant to wire it differently on a different board/ soldering - this will need to change

ENC_A = 17  # encoder channel A  (also called CLK)
ENC_B = 23  # encoder channel B  (also called DT)
DIR_PIN = 20  # goes to DRV-8825 DIR input (direction)
STEP_PIN = 18  # goes to DRV-8825 STEP input (must be 12/13/18/19 for HW-PWM)

PULSE_US = 1500  # micro-seconds HIGH and micro-seconds LOW for one pulse
# 500 µs high + 500 µs low → 1000 µs total means 1 kHz


COUNTS_PER_FULL_STEP = (
    41  # 8192 / 200 # 200 steps per revolution, 8192 counts per revolution
)
PULSE_US = 1500  # 1.5 ms high + 1.5 ms low

TEST_CLICKS = 164  # <- adjust after experiments:
# how many clicks from “closed”
# until gas starts hissing
VALVE_STEPS = 130  # how many steps to open/close the SodaStream valve (will change - time based test unlike the clicks)
TOL = 3  # acceptable error (clicks)

# start pigpio and connect to local daemon
pi = pigpio.pi()  # object that lets us call pigpio functions
if not pi.connected:  # If daemon isn’t running, leave
    raise SystemExit(
        "pigpiod (the pigpio daemon) is not running.\n"
        "Start it with: sudo systemctl start pigpiod"
    )

pi.wave_tx_stop()
pi.wave_clear()

# configuring the gpio pins
pi.set_mode(
    STEP_PIN, pigpio.OUTPUT
)  # the pin that tells the stepper motor to move one step
pi.write(
    STEP_PIN, 0
)  # keep STEP low when idle so that the motor does not move on its own
pi.set_mode(DIR_PIN, pigpio.OUTPUT)  # make DIR a digital output
pi.write(DIR_PIN, 0)  # default direction = 0 (CCW)

for pin in (ENC_A, ENC_B):
    pi.set_mode(pin, pigpio.INPUT)
    pi.set_pull_up_down(pin, pigpio.PUD_UP)  # Pi’s 50 k pull-ups
    pi.set_glitch_filter(pin, 5)  # 5 µs keeps every edge


# A pull-up means the Pi keeps the pin at logic 1 (3.3 V) until the encoder switch momentarily bridges it to ground (logic 0).
# This way we can detect the edges of the encoder signal; the reason they are pulled up is because the encoder
# is a switch that connects to ground when it is pressed, so we want to read a 1 when it is not pressed and a 0 when it is pressed
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(ENC_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# GPIO.setup(ENC_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)


actual = 0  # how many clicks the encoder says we have taken
last_a = pi.read(ENC_A)


def enc_cb(gpio, level, tick):
    global actual, last_a
    if level != last_a:  # any edge on A
        # 20 µs watchdog gives B time to settle
        t0 = time.perf_counter_ns()
        while (time.perf_counter_ns() - t0) < 5_000:
            pass
        direction = 1 if pi.read(ENC_B) != level else -1
        actual += direction
        last_a = level


pi.callback(ENC_A, pigpio.EITHER_EDGE, enc_cb)


def one_step(direction):
    """
    direction > 0 : clockwise
    direction < 0 : counter-clockwise
    Produces a clean one-shot pulse using pigpio ‘wave’ feature.
    """
    # aim the motor
    pi.write(DIR_PIN, 1 if direction > 0 else 0)

    # high then low on STEP

    pi.wave_clear()  # remove any old waves stored in pigpio

    wf = [
        pigpio.pulse(1 << STEP_PIN, 0, PULSE_US),  # HIGH for PULSE_US
        pigpio.pulse(0, 1 << STEP_PIN, PULSE_US),  # LOW for PULSE_US
    ]

    pi.wave_add_generic(wf)  # add our two pulses to the wave buffer
    wid = pi.wave_create()  # create a wave id (wid)

    pi.wave_send_once(wid)  # transmit the wave exactly once
    while pi.wave_tx_busy():  # wait until the wave is finished
        pass
    pi.wave_delete(wid)  # free memory


# main loop


def fixed_steps(n):
    dir_ = 1 if n > 0 else -1
    for _ in range(abs(n)):
        one_step(dir_)
        time.sleep(0.002)


def open_valve():  # CCW screw open
    fixed_steps(-VALVE_STEPS)


def close_valve():  # CW screw back
    fixed_steps(+VALVE_STEPS)


def goto(target):
    while abs(target - actual) > TOL:
        direction = 1 if target > actual else -1
        one_step(direction)
        time.sleep(0.0005)


def move_steps(n_steps):
    goto(actual + n_steps * COUNTS_PER_FULL_STEP)


def prompt():
    print(">>", end="", flush=True)


print("Commands:")
print("  f / b          one full step forward / back")
print("  open           open the valve (CCW)")
print("  close          close the valve (CW)")
print("  to N           goto absolute encoder click N")
print("  gas            goto TEST_CLICKS (found by experiment)")
print("  p              print encoder")
print("  q              quit")
prompt()

try:
    while True:
        cmd = input().strip().lower()[:5]

        if cmd == "f":
            one_step(+1)
        elif cmd == "b":
            one_step(-1)
        elif cmd.startswith("to "):
            try:
                goto(int(cmd.split()[1]))
            except ValueError:
                print("Usage: to 250")
        elif cmd == "gas":
            goto(TEST_CLICKS)
        elif cmd == "open":
            open_valve()
        elif cmd == "close":
            close_valve()
        elif cmd == "p":
            print(f"Encoder = {actual}")
        elif cmd == "q":
            break
        else:
            print("Unknown command.")
        prompt()

except KeyboardInterrupt:
    print("\nStopped")

finally:
    pi.wave_tx_stop()
    pi.stop()

# to start, run sudo systemctl start pigpiod
