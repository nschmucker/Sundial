# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example moves a servo its full range (180 degrees by default) and then back.

from board import SCL, SDA
from busio import I2C
from adafruit_servokit import ServoKit
# from adafruit_motor import servo
from adafruit_pca9685 import PCA9685
from time import sleep

i2c = I2C(SCL, SDA)
hat = PCA9685(i2c)
hat.frequency = 60

kit = ServoKit(channels=16)
kit.servo[15].angle = 180
kit.servo[15].angle = 90
# This is an example for the Standard servo - TowerPro SG-5010 - 5010:
#   https://www.adafruit.com/product/155
# servo0 = servo.Servo(hat.channels[0], min_pulse=600, max_pulse=2500)
# servo0 = servo.Servo(hat.channels[0])


# for i in range(180):
#     servo0.angle = i
# for i in range(180):
#     servo0.angle = 180 - i

led4 = hat.channels[4]

led4.duty_cycle = 0xffff
sleep(1)
led4.duty_cycle = 5000
sleep(1)
led4.duty_cycle = 0

hat.deinit() # TODO What is this