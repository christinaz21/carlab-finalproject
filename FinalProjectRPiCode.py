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
from gpiozero import PWMOutputDevice

#setting up the GPIO used for the fan
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)

#try catch so that exit behavior can be specified. 
try:
    #defines the motor hat and pin for the fan and flame sensor
    mh = Raspi_MotorHAT(0x70)
    fan_pin = 27
    flame_sensor = InputDevice(17)

    #specifies exit behavior of stepper motors 
    def turnOffStepper():
        #GPIO.output(fan_pin, GPIO.LOW)
        mh.getMotor(1).run(Raspi_MotorHAT.RELEASE)
        mh.getMotor(2).run(Raspi_MotorHAT.RELEASE)
        mh.getMotor(3).run(Raspi_MotorHAT.RELEASE)
        mh.getMotor(4).run(Raspi_MotorHAT.RELEASE)
        
    atexit.register(turnOffStepper)

    #defines the directions relative to the platform based on stepper rotation
    right = Raspi_MotorHAT.FORWARD
    left = Raspi_MotorHAT.BACKWARD

    #initializes the two stepper motors along with their speeds
    myStepper = mh.getStepper(200,1)
    myStepper.setSpeed(90)
    turntable = mh.getStepper(200, 2)
    turntable.setSpeed(90)
    steps = 105
    position = 0
    fireDetected = False
    facingRightDirection = False
    senseFlame = False
    sweeping = False

    def moveRight(amount):
        global position
        print("MOVING RIGHT")
        myStepper.step(steps*(amount), right, Raspi_MotorHAT.SINGLE)
        time.sleep(0.05)
        turnOffStepper()
        #keeps track of how much the stepper has moved right so that it can eventually go back home
        position += steps*(amount)

    def goHome():
        global position
        print("GOING HOME")
        #moves left by the position you have moved right
        myStepper.step(position, left, Raspi_MotorHAT.SINGLE)
        time.sleep(1)
        turnOffStepper()
        #reset the direction boolean
        facingRightDirection = False

    #turns the platform stepper 180 degrees 
    def turn180():
        turntable.step(steps, left, Raspi_MotorHAT.SINGLE)
        turnOffStepper()

    #camera initialization
    i2c = busio.I2C(board.SCL, board.SDA, frequency = 800000)

    mlx = adafruit_mlx90640.MLX90640(i2c)
    print("MLX addr detected on I2C", [hex(i) for i in mlx.serial_number])

    mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_2_HZ

    frame = [0] * 768

    #create figure
    fig, ax = plt.subplots()
    heatmap = ax.imshow(np.zeros((24,32)), cmap = 'hsv', vmin = 20, vmax = 40)
    plt.colorbar(heatmap)

    #function that turns on the fan on the platform
    def blow():
        GPIO.output(fan_pin, GPIO.HIGH)
        time.sleep(2)
        print("fan off")
        GPIO.output(fan_pin, GPIO.LOW)
        time.sleep(1)
        
    #the sweeping feedback loop
    def sweep(facingRightDirection):
        global sweeping
        global position
        global fireDetected
        counter = 0
        print("in sweep")
        #keep moving right until you sense the flame
        while(not senseFlame):
            #ensures that the platform doesn't move more than the conveyor belt allows
            counter = counter +1
            if(counter >10):
                break
            moveRight(1)
            #after you move right, check if the flame sensor has detected the fire. 
            if not flame_sensor.is_active:
                print("detected")
                #if it is facing the right direction, when it detects the fire it should turn right towards the fire and 
                #extinguish it
                if(facingRightDirection):
                    turntable.step(23, right, Raspi_MotorHAT.SINGLE)
                    turnOffStepper()
                    blow()
                    print("BLOWINGGGG")
                    time.sleep(1)
                    turntable.step(23, left, Raspi_MotorHAT.SINGLE)
                #otherwise turn left and reset
                else:
                    turntable.step(23, left, Raspi_MotorHAT.SINGLE)
                    turnOffStepper()
                    blow()
                    print("BLOWINGGGG")
                    time.sleep(1)
                    turntable.step(21, right, Raspi_MotorHAT.SINGLE)

                break
            time.sleep(0.25)
        #after the fire has been detected, go home and reset all booleans
        goHome()
        position = 0
        sweeping = False
        fireDetected = False
        return

    #function that is called that refreshes the camera
    def read_mlx90640():
        global fireDetected
        global facingRightDirection
        global sweeping
        global frame
        frame = [33] * 768
        try:
            mlx.getFrame(frame)
            print("updating frames")
        except ValueError:
            return None
        count = 0
        #calculating the average H location of the flame
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
        #Determines whether the flame sensor is facing the right direction or not
        if(fireDetected and averageH < 8):
            facingRightDirection = True
        else:
            facingRightDirection = False

        #turns if the flame sensor is not facing the right direction
        if(fireDetected and not facingRightDirection):
            facingRightDirection = False
            turn180()
            print("Sleeping")
            time.sleep(2)
            print("awake")

        #begin the sweeping feedback loop
        if(fireDetected and not sweeping):
            print("Begin sweeping!")
            sweep(facingRightDirection)
            if(not facingRightDirection):
                turn180()
                facingRightDirection = False
        
        print(fireDetected)
        GPIO.output(fan_pin, GPIO.LOW)

        return np.array(frame)

   
    #update the heatmap display and refresh the frames    
    def update_heatmap(*args):
        temp_data = read_mlx90640()
        if temp_data is not None:
            reshaped_data = temp_data.reshape((24,32))
            heatmap.set_array(reshaped_data)
        GPIO.output(fan_pin, GPIO.LOW)
        return heatmap,
        
    ani = animation.FuncAnimation(fig, update_heatmap, interval = 500)

    plt.show()

#cleaning up when exiting
except KeyboardInterrupt:
    print("exiting...")
    GPIO.output(fan_pin, GPIO.LOW)
    time.sleep(1)
    print("exited")
    GPIO.cleanup()
    
