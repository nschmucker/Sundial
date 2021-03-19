import board
import busio
import adafruit_pca9685
from adafruit_servokit import ServoKit

i2c = busio.I2C(board.SCL, board.SDA)
hat = adafruit_pca9685.PCA9685(i2c)
hat.frequency = 60
led_channel = hat.channels[0] # Set this to the right channel
led_channel.duty_cycle = 0xffff # Brightness from 0 to 0xffff (16-bit value)

kit = ServoKit(channels=16)
kit.servo[].angle = 45 # 0-180; # Set this to the right channel