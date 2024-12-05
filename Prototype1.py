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


mh = Raspi_MotorHAT(0x70)

def turnOffStepper():
    mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
    mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)
    
atexit.register(turnOffStepper)

right = Raspi_MotorHAT.BACKWARD
left = Raspi_MotorHAT.FORWARD
myStepper = mh.getStepper(200,1)
myStepper.setSpeed(90)
turntable = mh.getStepper(200, 2)
turntable.setSpeed(90)
one_note = 112
position = 0
fireDetected = False
facingRightDirection = False

def moveRight(note):
    global position
    print("MOVING RIGHT")
    myStepper.step(one_note*(note), right, Raspi_MotorHAT.SINGLE)
    time.sleep(1)
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
    turntable.step(105, left, Raspi_MotorHAT.SINGLE)
    turnOffStepper()

#turn180()

i2c = busio.I2C(board.SCL, board.SDA, frequency = 800000)

mlx = adafruit_mlx90640.MLX90640(i2c)
print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

frame = [0] * 768

#create figure
fig, ax = plt.subplots()
heatmap = ax.imshow(np.zeros((24,32)), cmap = 'hsv', vmin = 20, vmax = 40)
plt.colorbar(heatmap)

def read_mlx90640():
    global fireDetected
    global facingRightDirection
    try:
        mlx.getFrame(frame)
    except ValueError:
        return None
    count = 0
    averageH = -1;
    for h in range(24):
        for w in range(32):
            t = frame[h*32 + w]
            if(t>34):
                print(t," ", h, " ",w)
                averageH += h
                fireDetected = True
                count+=1;
    
    if(count != 0):
        averageH = averageH / count
    
    #Code to simulate facing forward or backward stepper movement
    if(fireDetected and averageH > 8):
        facingRightDirection = True
    
    if(fireDetected and not facingRightDirection):
        turn180()
        facingRightDirection = True
    #Code to simulate side to side stepper movement
    if(fireDetected):
        moveRight(1)
    if(fireDetected == True and count == 0):
        fireDetected = False
        goHome()
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


