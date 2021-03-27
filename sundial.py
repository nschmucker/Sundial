"""
sundial.py
This file contains code to run an indoor sundial
Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from pysolar.solar import get_altitude, get_azimuth
from scipy.optimize import fsolve
from numpy import isclose
from math import cos, sin, tan, pi

from board import SCL, SDA
from busio import I2C
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

import requests

from time import sleep

import datetime

i2c = I2C(SCL, SDA)
hat = PCA9685(i2c)
hat.frequency = 50
led4 = hat.channels[4]
servo_alt = servo.Servo(hat.channels[13], min_pulse=600, max_pulse=2500)
servo_az = servo.Servo(hat.channels[15], min_pulse=600, max_pulse=2500)


GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
ARM_LOC = (0, -2, 1)
ARM_LENGTH = 5

# Independence Hall
LAT =  39.95
LON = -75.15

gnomon = {
    "loc": GNOMON_LOC,
    "length": GNOMON_LENGTH,
    "alt": 0, # radians, relative to horizon
    "az": 0 # radians, relative to north
}
arm = {
    "loc": ARM_LOC,
    "length": ARM_LENGTH,
    "alt": 0, # radians, relative to horizon
    "az": 0  # radians, relative to north
}
last_sunrise = {
    "alt": -0.1,
    "az": 2.1,
    "t": 4.3
}
guess = {
    "alt": -0.6,
    "az": 4.5,
    "t": 4.3
}
times = {
    "now": datetime.datetime.now(datetime.timezone.utc),
    "last_sunrise": datetime.datetime(2021, 3, 14, 11, 3, tzinfo=datetime.timezone.utc)
}

API_KEY = "YDgMefVz29eKGJtUF9g1W6LxjFVh8o0U"
BASE_URL = "https://data.climacell.co/v4/timelines?"
URL = BASE_URL + \
      "location=" + str(LAT) + "," + str(LON) + \
      "&fields=cloudCover" + \
      "&timesteps=current" + \
      "&apikey=" + API_KEY 

def get_cloudcover():
    r = requests.get(URL)
    j = r.json()
    cloud_cover = j["data"]["timelines"][0]["intervals"][0]["values"]["cloudCover"]/100
    
    return cloud_cover

def mimic_clouds(raw_val):
    pct_sun = 1 - get_cloudcover()
    pct_to_adj = 0.8 + 0.2*pct_sun
    adj_val = int(int(raw_val)*pct_to_adj)
    
    return adj_val

is_led_on = gnomon["alt"] >= 0
def update_leds():
    brightness = 0xffff if is_led_on else 0
    adjusted_brightness = mimic_clouds(brightness)
    
    led4.duty_cycle = adjusted_brightness
    print(adjusted_brightness)

class Servo:
    """ This class is for all servos
        angle in range [0, 180] (degrees) """

    def __init__(self, angle):
        self.angle = angle

    def update(self):
        print(str(self.angle))

def func(vars):
    alt, az, t = vars
    return [(arm["loc"][0] + arm["length"]*cos(alt)*cos(az-pi/2)) - (gnomon["loc"][0] + t*cos(gnomon["az"]-pi/2)),
            (arm["loc"][1] + arm["length"]*cos(alt)*sin(az-pi/2)) - (gnomon["loc"][1] + t*sin(gnomon["az"]-pi/2)),
            (arm["loc"][2] + arm["length"]*sin(alt)) - (gnomon["loc"][2] + t*tan(gnomon["alt"]))]

def validate_fsolve(x):
    finds_zeros = all(isclose(func(x), [0.0, 0.0, 0.0]))
    positive_t = x[2] >= 0

    return (finds_zeros and positive_t)

def rotate_angle(angle, min_val, max_val):
    a = angle
    while a < min_val: a += 2*pi
    while a > max_val: a += -2*pi

    return a

servo_alt = Servo(0)
servo_az = Servo(180)



unstable_math = False
while not unstable_math:
    times["now"] = datetime.datetime.now(datetime.timezone.utc)
    
    # Get sun's location at current time (in radians)
    gnomon["alt"] = get_altitude(LAT, LON, times["now"])*pi/180
    gnomon["az"] = get_azimuth(LAT, LON, times["now"])*pi/180
    
    if gnomon["alt"] < 0:
        # Sleep until 10 minutes before this morning's sunrise
        #  and then increments of 1 minute until sunrise
        if is_led_on:
            sleep_time = times["last_sunrise"] + datetime.timedelta(days=1, minutes=-10) - times["now"]
        else:
            sleep_time = datetime.timedelta(minutes=1)
        
        # Prep our next guess to be the last sunrise alt/az/t
        guess["alt"] = last_sunrise["alt"]
        guess["az"] = last_sunrise["az"]
        guess["t"] = last_sunrise["t"]
        
        # Light off and servos to home position
        is_led_on = False
        servo_alt.angle = 135
        servo_az.angle = 90
        
        # Update the physical sundial
        update_leds()
        servo_alt.update()
        servo_az.update()
        
        sleep(int(sleep_time))
        
    else:
        # Calculate sun's location relative to arm pivot point
        root = fsolve(func, (guess["alt"], guess["az"], guess["t"]))

        # Validate fsolve worked and then continue with updates
        if validate_fsolve(root):
            # Move our alt and az to be in the correct range
            arm["alt"] = rotate_angle(root[0], -pi/2, pi/2)
            arm["az"] = rotate_angle(root[1], pi/2, 3*pi/2)
            
            # If the sun is coming up, refresh our best guess for sunrise time/alt/az/t
            if not is_led_on:
                times["last_sunrise"] = times["now"]
                last_sunrise["alt"] = arm["alt"]
                last_sunrise["az"] = arm["az"]
                last_sunrise["t"] = root[2]
            
            # Prep our next guess to be the latest solution
            guess["alt"] = arm["alt"]
            guess["az"] = arm["az"]
            guess["t"] = root[2]

            # Light on and servos to appropriate position
            is_led_on = True
            servo_alt.angle = (arm["alt"]+pi/2)*180/pi
            servo_az.angle = (arm["az"]-pi/2)*180/pi
                        
            # Update the physical sundial
            servo_alt.update()
            servo_az.update()
            update_leds()

            # Sleep 10 minutes
            sleep(60*10) # TODO: What is the resolution of the servos?
            
        else:
            unstable_math = True

# Light off and servos to home position
is_led_on = False
servo_alt.angle = 135
servo_az.angle = 90

# Update the physical sundial
update_leds()
servo_alt.update()
servo_az.update()
