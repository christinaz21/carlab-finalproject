from gpiozero import PWMOutputDevice
from time import sleep
import RPi.GPIO as GPIO


# Using GPIO 27 for the fan
fan_pin = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(fan_pin, GPIO.OUT)

#fan = PWMOutputDevice(27)

try:
    while True:
        print("fan on at 50% speed")
        GPIO.output(fan_pin, GPIO.HIGH)
        #fan.value = 0.50
        sleep(1)
        print("fan off")
        GPIO.output(fan_pin, GPIO.LOW)
        #fan.off()
        #fan.close()
        sleep(2)
        
except KeyboardInterrupt:
    print("exiting...")
    GPIO.output(fan_pin, GPIO.LOW)
    #fan.off()
    #fan.close()
finally:
    GPIO.output(fan_pin, GPIO.LOW)

    #GPIO.cleanup()