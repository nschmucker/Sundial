from board import SCL, SDA
from busio import I2C
from adafruit_pca9685 import PCA9685
from time import sleep

i2c = I2C(SCL, SDA)
hat = PCA9685(i2c)
hat.frequency = 60
led_channel = hat.channels[4]

led_channel.duty_cycle = 0xffff
sleep(2)
led_channel.duty_cycle = 5000
sleep(2)
led_channel.duty_cycle = 0