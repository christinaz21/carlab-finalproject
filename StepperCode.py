import smbus2
from Raspi_MotorHAT import Raspi_MotorHAT
import RPi.GPIO as GPIO
import time
import atexit


mh = Raspi_MotorHAT(0x70)

def turnOffStepper():
    mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)
    
atexit.register(turnOffStepper)

right = Raspi_MotorHAT.FORWARD
left = Raspi_MotorHAT.BACKWARD
myStepper = mh.getStepper(200,1)
myStepper.setSpeed(90)
turntable = mh.getStepper(200, 2)
turntable.setSpeed(90)
one_note = 112
position = 0

def moveRight(note):
    myStepper.step(one_note*(note), right, Raspi_MotorHAT.SINGLE)
    time.sleep(1)
    turnOffStepper()
    position = one_note*(note)
    #position = position - 1
    
def moveLeft(note):
    myStepper.step(one_note*(note), left, Raspi_MotorHAT.SINGLE)
    time.sleep(1)
    turnOffStepper()
    position = one_note*(note)
    #position = position - 1
    

    
    
try:
    #moveRight(1)
    
    turntable.step(105, left, Raspi_MotorHAT.DOUBLE)
    time.sleep(1)
    turntable.step(105, right, Raspi_MotorHAT.DOUBLE)
    turnOffStepper()
    #moveRight(4)
    

except KeyboardInterrupt:
    GPIO.cleanup()
