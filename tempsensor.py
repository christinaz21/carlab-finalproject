import RPi.GPIO as GPIO
from gpiozero import InputDevice
import time

# try:
#     # GPIO SETUP
#     channel = 21
#     GPIO.setmode(GPIO.BCM)
#     GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# 
#     def callback(channel):
#         print("flame detected")
#     
#     #GPIO.add_event_detect(channel, GPIO.BOTH)
#     #GPIO.add_event_callback(channel, callback)
# 
#     while True:
#         print(GPIO.input(channel))
#         time.sleep(0.1)
#         
# 
# except KeyboardInterrupt:
#     print("exiting...")
# finally:
#     GPIO.cleanup()


flame_sensor = InputDevice(17)

while True:
    if flame_sensor.is_active:
        print("no flame detected")
    else:
        print("flame detected")
    time.sleep(1)

