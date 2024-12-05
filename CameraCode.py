import time
import board
import busio
import adafruit_mlx90640
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

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
    try:
        mlx.getFrame(frame)
    except ValueError:
        return None
    for h in range(24):
        for w in range(32):
            t = frame[h*32 + w]
            if(t>34):
                print(t," ", h, " ",w)
    return np.array(frame)

def update_heatmap(*args):
    temp_data = read_mlx90640()
    if temp_data is not None:
        reshaped_data = temp_data.reshape((24,32))
        heatmap.set_array(reshaped_data)
    return heatmap,

ani = animation.FuncAnimation(fig, update_heatmap, interval = 500)

plt.show()

#while True:
#    try:
#        mlx.getFrame(frame)
#    except ValueError:
#        continue
#    
#    for h in range(24):
#        for w in range(32):
#            t = frame[h*32 + w]
#            print("%0.1f, " % t, end = "")
#        print()
#    print()