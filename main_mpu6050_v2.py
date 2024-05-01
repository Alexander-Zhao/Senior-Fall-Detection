#Shows Pi is on by turning on LED when plugged in
LED = machine.Pin("LED", machine.Pin.OUT)
LED.on()

from imu import MPU6050
from time import sleep
from machine import Pin, I2C
import math
import time

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
imu = MPU6050(i2c)

#def detect_fall(acceleration_data, threshold=2.0):
#    magnitude = np.linalg.norm(acceleration_data)
#    if magnitude > threshold:
#        return True
#    else:
#        return False

roll = 0
pitch = 0
yaw = 0
tLoop = 0
cnt = 0

while True:
    tStart = time.ticks_ms()
    ax=round(imu.accel.x,2)
    ay=round(imu.accel.y,2)
    az=round(imu.accel.z,2)

#Calibration for az is ( m= -0.04300329, b = 0.04542932)
    az_offset = -0.04300329 * az + 0.04542932
    az_after_calib = az - az_offset
    
    gx=round(imu.gyro.x, 2)
    gy=round(imu.gyro.y, 2)
    gz=round(imu.gyro.z, 2)

#Calibration for Gyro is Complete! 13958 points total
#[-1.175684, -1.646084, -0.3335816]
    gx_calibration = -1.175684
    gy_calibration = -1.646084
    gz_calibration = -0.3335816
 
    gx_after_calib = gx - gx_calibration
    gy_after_calib = gy - gy_calibration
    gz_after_calib = gz - gz_calibration

#    print('xGyro',gx_after_calib,'yGyro', gy_after_calib,'zGyro', gz_after_calib)
    roll = roll + gy_after_calib * tLoop
    pitch = pitch + gx_after_calib * tLoop
    yaw = yaw + gz_after_calib * tLoop      
    

# Example usage:
 #   is_fall = detect_fall(acceleration_data)
 #   print("Fall Detected:", is_fall)


    tem=round(imu.temperature,2)
#   print("ax G",ax,"\t","ay G",ay,"\t","az G",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t",        ",end="\r")
#   print("ax G",ax,"\t","ay G",ay,"\t","az G",az,"\t","gx",gx,"\t","gy",gy,"\t","gz",gz,"\t\n")
#    print("az",az,"\t","az_after_calib",az_after_calib,"\t", "gx",gx,"\t","gx_after_calib",gx_after_calib,"\t","gy",gy,"\t","gy_after_calib",gy_after_calib,"\t","gz",gz,"\t","gz_after_calib",gz_after_calib,"\t\n")

    sleep(0.2)
    
    cnt = cnt + 1
    if cnt == 50 :
        cnt = 0
        print ("roll",roll, "pitch",pitch,"yaw",yaw )
        
    tStop = time.ticks_ms()
    tLoop = (tStop - tStart) * 0.01
    