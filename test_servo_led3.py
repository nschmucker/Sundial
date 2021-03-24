# https://circuitpython.readthedocs.io/projects/pca9685/en/latest/examples.html

from board import SCL, SDA
from busio import I2C
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo
from time import sleep

i2c = I2C(SCL, SDA)
hat = PCA9685(i2c)
hat.frequency = 50
led4 = hat.channels[4]
# This is an example for the Standard servo - TowerPro SG-5010 - 5010:
#   https://www.adafruit.com/product/155
servo15 = servo.Servo(hat.channels[15], min_pulse=600, max_pulse=2500)
# servo15 = servo.Servo(hat.channels[15])

led4.duty_cycle = 0xffff
servo15.angle = 45
sleep(1)
servo15.angle = 135
sleep(1)
led4.duty_cycle = 0

hat.deinit()
