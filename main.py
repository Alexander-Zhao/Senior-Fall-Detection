# import modules
from imu import MPU6050
from machine import I2C, Pin
from utime import sleep, ticks_ms, ticks_diff
from ssd1306 import SSD1306_I2C

# Library needed for BLE to Mobile App communication
# https://github.com/makeuseofcode/Raspberry-Pi-Pico-W-WH-Bluetooth-Example-in-MicroPython/blob/main/ble_simple_peripheral.py
# This example demonstrates a UART periperhal.
import bluetooth
import random
import struct
import time
from ble_simple_peripheral import BLESimplePeripheral

# https://www.uuidgenerator.net/
#2bff5e11-77ba-4f7a-a35a-761e5ba12836
#6d4ff53b-c85e-4e94-8a22-6c860a6ab6ef
#d935a1bb-0c55-484e-948c-ad7c8f97dddd
#2561fbc3-41cf-4d6b-93e6-37d780c6eb52

# setup I2C bus and mpu
i2c = I2C(0, sda=Pin(16), scl=Pin(17), freq=400000)
mpu = MPU6050(i2c)

# setup I2C bus and OLED display
i2c2=I2C(1, sda = Pin(2), scl = Pin(3), freq = 400000)
myOLED = SSD1306_I2C(128, 64, i2c2, addr = 0x3c)
myOLED.init_display()

# indicator variable for a drop
drop_detected = False
#research published in the journal "Age and Ageing" suggests that
#a significant portion of falls among the elderly occur during
# level walking, and the average fall height in these cases is
#around 60-80 cm (approximately 2-2.5 feet).
#in this project,  set default fall threshold as 20 inches

fall_threshold_inch = 20
fall_height = 0
fall_detected = False


#Generate an instance of BLESimplePeripheral
ble = bluetooth.BLE()
Peripheral = BLESimplePeripheral(ble)

# Function to detect drop
def detect_drop():
    zAccel = mpu.accel.z
    return zAccel < 0.95  # Adjust the threshold as needed

# Function to measure fall height
def measure_drop_height(startTime, stopTime):
    # Convert drop time from ms to seconds
    dropTime = ticks_diff(stopTime, startTime)/1000  
    # Calculate fall height based on the duration
    # Assuming gravity is 9.81 m/s^2

    distance_inches = 0.5 * (32.17405 * 12) * (dropTime**2)
    distance_cm = 0.5 * 980.665 * (dropTime**2)
    # put results on OLED
    myOLED.fill(0)
    myOLED.text("Drop Distance:", 0, 0)
    # use f-string to create string to print to OLED
    inch_text = f'inches: {distance_inches:3.1f}'
    myOLED.text(inch_text, 0, 16)
    # use f-string to create string to print to OLED
    cm_text = f'cm: {distance_cm:3.1f}'
    myOLED.text(cm_text, 0, 32)
    myOLED.show()
    
    return distance_inches

# while true loop will continuely update startTime and stopTime
# until a drop occurs indicated by zAccel dropping below 0.95G
while True:
    zAccel = mpu.accel.z
    myOLED.fill(0)
    myOLED.text('Drop when ready', 0, 0)
    myOLED.show()
    startTime = ticks_ms()
    while zAccel < 0.95:
        # a drop has occurred stay in this loop till zAccel gets back to 1G
        zAccel = mpu.accel.z  
        drop_detected = True
        sleep(0.001)
    stopTime = ticks_ms()      
    if drop_detected == True:
        print("Drop detected \n") 
        fall_height = measure_drop_height(startTime, stopTime)
        fall_height = round(fall_height)
        print("Drop heigh detected fall_height",fall_height)
        
         # must sleep a second or so to not register bouncing around after the drop

        # Send fall detection data over BLE
        #data = struct.pack("<f", fall_height)  # Pack fall height as float (4 bytes)
        #characteristic.write_value(data)
        if fall_height >= fall_threshold_inch:
            detect_text = ('Fall Detected!')
            myOLED.text(detect_text, 0, 48)
            myOLED.show()
            if Peripheral.is_connected():
                print("BLE is connected")
        
                data = str(fall_height).encode()
                Peripheral.send(data)
        sleep(3) #end of if drop_detected == True:
        
    drop_detected = False
    fall_height = 0
    time.sleep_ms(1000)