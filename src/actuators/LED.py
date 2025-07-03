from gpiozero import LED
from signal import pause

my_led = LED(17)
my_led.blink()
pause()
# my_led.off()
