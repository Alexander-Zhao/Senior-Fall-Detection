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
from ble_advertising import advertising_payload
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)


class BLESimplePeripheral:
    def __init__(self, ble, name="Fall-Detect"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection. Alsways connects when there is an available node.
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=50000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback

    def on_rx(v):
        print("RX", v)

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
fall_detected = False


#Generate an instance of BLESimplePeripheral
ble = bluetooth.BLE()
Peripheral = BLESimplePeripheral(ble)

# Function to detect drop
def detect_drop():
    zAccel = mpu.accel.z
    return zAccel < 0.95  # Adjust the threshold as needed

# Function to measure fall height
def measure_drop_height():
    startTime = ticks_ms()
    while detect_drop():
        # Continue measuring until the fall ends
        sleep(0.001)
    stopTime = ticks_ms()
    
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
    if detect_drop():
        print("Detected Drop")
        drop_detected = True
        fall_height = measure_drop_height()
        print("Drop heigh detected fall_height",fall_height)
        
        # Send fall detection data over BLE
        #data = struct.pack("<f", fall_height)  # Pack fall height as float (4 bytes)
        #characteristic.write_value(data)
    else:
        drop_detected = False
    # must sleep a second or so to not register bouncing around after the drop
    sleep(5)
    # reset drop detection
    myOLED.fill(0)
    myOLED.text('Drop when ready', 0, 0)
    myOLED.show()
    sleep(0.001)