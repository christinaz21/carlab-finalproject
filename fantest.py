from gpiozero import PWMOutputDevice
from time import sleep

# Using GPIO 27 for the fan
fan = PWMOutputDevice(27)

try:
    while True:
        print("fan on at 50% speed")
        fan.value = 0.99
        sleep(5)
        print("fan off")
        fan.off()
        sleep(5)
        
except KeyboardInterrupt:
    print("exiting...")
    fan.off()