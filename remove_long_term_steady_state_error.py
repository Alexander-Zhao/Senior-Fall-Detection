from imu import MPU6050
from machine import I2C,Pin
import math
import time
 
i2c=I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
mpu = MPU6050(i2c)
 
rollG=0
pitchG=0
 
rollComp=0
pitchComp=0
 
errorR=0
errorP=0
 
yaw=0
tLoop=0
cnt=0
 
while True:
    tStart=time.ticks_ms()
    
    xGyro=mpu.gyro.x
    yGyro=-mpu.gyro.y
    zGyro=mpu.gyro.z
    
    xAccel=mpu.accel.x
    yAccel=mpu.accel.y
    zAccel=mpu.accel.z
    
    rollG=rollG+yGyro*tLoop
    pitchG=pitchG+xGyro*tLoop
    
    rollA=math.atan(xAccel/zAccel)/2/math.pi*360
    pitchA=math.atan(yAccel/zAccel)/2/math.pi*360
    
    rollComp= rollA*.005 + .995*(rollComp+yGyro*tLoop)+errorR*.005
    pitchComp= pitchA*.005 + .995*(pitchComp+xGyro*tLoop)+errorP*.005
    
    errorP=errorP + (pitchA-pitchComp)*tLoop
    errorR=errorR + (rollA-rollComp)*tLoop
    
    cnt=cnt+1
    if cnt==10:
        cnt=0
        print('Roll_Gyro:',rollA, 'Roll_Gyro_Steady_Error: ',rollComp, 'Pitch_Gyro: ',pitchA,'Pitch_Gyro_Steady_Error: ',pitchComp)
        #print('RA: ',rollA,'RC: ',rollComp)
    tStop=time.ticks_ms()
    tLoop=(tStop-tStart)*.001