import smbus2
import time
import board
import busio
from Raspi_MotorHAT import Raspi_MotorHAT
import RPi.GPIO as GPIO
import atexit
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from gpiozero import InputDevice


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
fireDetected = False
facingRightDirection = False
senseFlame = False
sweeping = False
flame_sensor = InputDevice(17)


def moveRight(note):
    global position
    print("MOVING RIGHT")
    myStepper.step(one_note*(note), right, Raspi_MotorHAT.SINGLE)
    time.sleep(0.1)
    turnOffStepper()
    position += one_note*(note)
    
    
def moveLeft(note):
    myStepper.step(one_note*(note), left, Raspi_MotorHAT.SINGLE)
    time.sleep(1)
    turnOffStepper()

    
def goHome():
    global position
    print("GOING HOME")
    myStepper.step(position, left, Raspi_MotorHAT.SINGLE)
    time.sleep(1)
    turnOffStepper()
    facingRightDirection = False
    
def turn180():
    turntable.step(105, right, Raspi_MotorHAT.SINGLE)
    turnOffStepper()


i2c = busio.I2C(board.SCL, board.SDA, frequency = 800000)

mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

frame = [0] * 768

#create figure
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((24,32)), cmap = 'hsv', vmin = 20, vmax = 40)
plt.colorbar(heatmap)

def sweep(facingRightDirection):
    global sweeping
    global position
    global fireDetected
    #global averageH
    #print(averageH)
    #if(fireDetected and averageH >5):
    #    print("WRONG DIR")
    #    turntable.step(105, right, Raspi_MotorHAT.SINGLE)
    #    turnOffStepper()
    counter = 0
    print("in sweep")
    while(not senseFlame):
        counter = counter +1
        if(counter >10):
            break
        moveRight(1)
        if not flame_sensor.is_active:
            print("detected")
            if(facingRightDirection):
                turntable.step(15, right, Raspi_MotorHAT.SINGLE)
                turnOffStepper()
                print("BLOWINGGGG")
                time.sleep(1)
                turntable.step(15, left, Raspi_MotorHAT.SINGLE)
            else:
                turntable.step(15, left, Raspi_MotorHAT.SINGLE)
                turnOffStepper()
                print("BLOWINGGGG")
                time.sleep(1)
                turntable.step(15, right, Raspi_MotorHAT.SINGLE)

            break
        time.sleep(0.5)
    goHome()
    position = 0
    sweeping = False
    fireDetected = False
    return
    
def read_mlx90640():
    global fireDetected
    global facingRightDirection
    global sweeping
    global frame
    frame = [33] * 768
    try:
        #for i in range(3):
        mlx.getFrame(frame)
        print("updating frames")
    except ValueError:
        return None
    count = 0
    averageH = -1;
    for h in range(24):
        for w in range(32):
            t = frame[h*32 + w]
            if(t>36):
                print(t," ", h, " ",w)
                averageH += h
                fireDetected = True
                count+=1;
    
    if(count != 0):
        averageH = averageH / count
    
    print(averageH)
    #Code to simulate facing forward or backward stepper movement
    if(fireDetected and averageH < 5):
        facingRightDirection = True
    else:
        facingRightDirection = False
    
    if(fireDetected and not facingRightDirection):
        facingRightDirection = False
        turn180()
        print("Sleeping")
        time.sleep(5)
        print("awake")
        #facingRightDirection = True
        
    if(fireDetected and not sweeping):
        print("Begin sweeping!")
        #sweeping = True
        sweep(facingRightDirection)
        if(not facingRightDirection):
            turntable.step(105, left, Raspi_MotorHAT.SINGLE)
            turnOffStepper()
            facingRightDirection = False
    
    print(fireDetected)
    return np.array(frame)

def update_heatmap(*args):
    temp_data = read_mlx90640()
    if temp_data is not None:
        reshaped_data = temp_data.reshape((24,32))
        heatmap.set_array(reshaped_data)
    return heatmap,

ani = animation.FuncAnimation(fig, update_heatmap, interval = 500)

plt.show()



