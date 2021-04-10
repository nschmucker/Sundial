# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# This example moves a servo its full range (180 degrees by default) and then back.

from board import SCL, SDA
from busio import I2C

# This example also relies on the Adafruit motor library available here:
# https://github.com/adafruit/Adafruit_CircuitPython_Motor
from adafruit_motor import servo

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

i2c = I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
hat = PCA9685(i2c)
hat.frequency = 50

# This is an example for the Standard servo - TowerPro SG-5010 - 5010:
#   https://www.adafruit.com/product/155
# servo0 = servo.Servo(pca.channels[0], min_pulse=600, max_pulse=2500)
servo0 = servo.Servo(hat.channels[15])

for i in range(180):
    servo0.angle = i
for i in range(180):
    servo0.angle = 180 - i
#hat.deinit()