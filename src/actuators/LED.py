from signal import pause

from gpiozero import LED

my_led = LED(17)
my_led.blink()
pause()
# my_led.off()
