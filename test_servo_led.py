import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit
from time import sleep

i2c = busio.I2C(board.SCL, board.SDA)
hat = adafruit_pca9685.PCA9685(i2c)
hat.frequency = 60
led_channel = hat.channels[4] # Set this to the right channel

kit = ServoKit(channels=16)
kit.servo[15].angle = 45 # 0-180; # Set this to the right channel
sleep(1)
led_channel.duty_cycle = 0xffff # Brightness from 0 to 0xffff (16-bit value)
sleep(1)
kit.servo[15].angle = 135 # 0-180
sleep(1)
led_channel.duty_cycle = 0