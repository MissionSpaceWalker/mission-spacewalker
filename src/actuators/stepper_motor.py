import time
import threading            
import pigpio

class StepperMotor:
    def __init__(self, pi, step_pin=18, dir_pin=25, enc_a=17, enc_b=23):
        self.pi = pi
        self.STEP_PIN = step_pin
        self.DIR_PIN  = dir_pin
        self.ENC_A    = enc_a
        self.ENC_B    = enc_b

        self.PULSE_US = 1300
        self.COUNTS_PER_FULL_STEP = 41
        self.VALVE_STEPS = 130
        self.TEST_CLICKS = 164
        self.TOL = 3

        self.actual = 0
        self.last_a = 0

        self._stop_event = threading.Event()   # shared stop flag (thread-safe)

        self._setup_pins()
        self._setup_encoder()

    def _setup_pins(self):
        self.pi.set_mode(self.STEP_PIN, pigpio.OUTPUT)
        self.pi.write(self.STEP_PIN, 0)
        self.pi.set_mode(self.DIR_PIN, pigpio.OUTPUT)
        self.pi.write(self.DIR_PIN, 0)

    def _setup_encoder(self):
        for pin in (self.ENC_A, self.ENC_B):
            self.pi.set_mode(pin, pigpio.INPUT)
            self.pi.set_pull_up_down(pin, pigpio.PUD_UP)
            self.pi.set_glitch_filter(pin, 5)
        self.last_a = self.pi.read(self.ENC_A)

        self.pi.callback(self.ENC_A, pigpio.EITHER_EDGE, self._enc_cb)

    def _enc_cb(self, gpio, level, tick):
        if level != self.last_a:
            # small debounce window
            t0 = time.perf_counter_ns()
            while (time.perf_counter_ns() - t0) < 5_000:
                pass
            direction = 1 if self.pi.read(self.ENC_B) != level else -1
            self.actual += direction
            self.last_a = level

    # ---------- MOTION PRIMITIVES WITH COOPERATIVE STOP ----------

    def _send_one_pulse(self):
        """Send one STEP pulse via pigpio wave.
        Returns False if a stop was requested before or during the pulse.
        """
        if self._stop_event.is_set():      
            return False

        self.pi.wave_clear()
        wf = [
            pigpio.pulse(1 << self.STEP_PIN, 0, self.PULSE_US),
            pigpio.pulse(0, 1 << self.STEP_PIN, self.PULSE_US),
        ]
        self.pi.wave_add_generic(wf)
        wid = self.pi.wave_create()
        if wid < 0:                            # guard for allocation failure
            return False

        self.pi.wave_send_once(wid)

        # busy-wait but allow interruption mid-pulse
        while self.pi.wave_tx_busy():
            if self._stop_event.is_set():
                self.pi.wave_tx_stop()       
                break
            time.sleep(0.0002)

        self.pi.wave_delete(wid)               # keep wave pool clean
        return not self._stop_event.is_set()

    def one_step(self, direction):
        if self._stop_event.is_set():        
            return False
        self.pi.write(self.DIR_PIN, 1 if direction > 0 else 0)
        return self._send_one_pulse()    

    def fixed_steps(self, n):
        self._stop_event.clear()              
        dir_ = 1 if n > 0 else -1
        for _ in range(abs(n)):
            if not self.one_step(dir_):        # break if STOP was requested
                break
            time.sleep(0.002)

    def open_valve(self):
        self.fixed_steps(-self.VALVE_STEPS)

    def close_valve(self):
        self.fixed_steps(+self.VALVE_STEPS)

    def goto(self, target):
        self._stop_event.clear()               # allow new motion
        while not self._stop_event.is_set() and abs(target - self.actual) > self.TOL:
            direction = 1 if target > self.actual else -1
            if not self.one_step(direction):   # break if STOP requested mid-move
                break
            time.sleep(0.0005)

    def move_steps(self, n_steps):
        self.goto(self.actual + n_steps * self.COUNTS_PER_FULL_STEP)

    def stop(self):
        """Stop immediately: set flag, cancel in-flight wave, force STEP low."""
        self._stop_event.set()              
        self.pi.wave_tx_stop()                 
        self.pi.write(self.STEP_PIN, 0)       
