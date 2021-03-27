"""
sundial.py
This file contains code to run an indoor sundial
Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from busio import I2C
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

from pysolar.solar import get_altitude, get_azimuth
from scipy.optimize import fsolve
from numpy import isclose
from math import cos, sin, tan, pi

import requests
import datetime
from time import sleep


# --- Global constants; update to reflect physical sundial ---
GNOMON_LOC = (0, 0, 0) # By definition, center on gnomon tip
GNOMON_LENGTH = None
ARM_LOC = (0, -2, 1)   # Pivot point of movable arm
ARM_LENGTH = 5         # Consistent units with ARM_LOC

# Independence Hall
LAT =  39.95 
LON = -75.15 

API_KEY = "YDgMefVz29eKGJtUF9g1W6LxjFVh8o0U"
BASE_URL = "https://data.climacell.co/v4/timelines?"
URL = BASE_URL + \
      "location=" + str(LAT) + "," + str(LON) + \
      "&fields=cloudCover" + \
      "&timesteps=current" + \
      "&apikey=" + API_KEY


# --- Variables; need to update for initial code execution ---
#     See helper_sundial_inputs.py
gnomon = {
    "loc": GNOMON_LOC,
    "length": GNOMON_LENGTH,
    "alt": 0, # radians, relative to horizon
    "az": 0   # radians, relative to north
}
arm = {
    "loc": ARM_LOC,
    "length": ARM_LENGTH,
    "alt": 0, # radians, relative to horizon
    "az": 0   # radians, relative to north
}
last_sunrise = {
    "alt": -0.2,
    "az": 1.9,
    "t": 4.6
}
guess = {
    "alt": 0.4,
    "az": 2.8,
    "t": 2.8
}
times = {
    "now": datetime.datetime.now(datetime.timezone.utc),
    "last_sunrise": datetime.datetime(2021, 3, 27, 10, 42, tzinfo=datetime.timezone.utc)
}

is_led_on = gnomon["alt"] >= 0


# --- Functions ---
def get_cloudcover():
    """Helper function to retrieve current cloudcover
    
    Uses climacell API: https://docs.climacell.co/reference/welcome
    """
    
    r = requests.get(URL)
    j = r.json()
    cloud_cover = j["data"]["timelines"][0]["intervals"][0]["values"]["cloudCover"]/100
    
    return cloud_cover # [0,1]

def mimic_clouds(raw_val):
    """Helper function to adjust LED brightness for cloudcover

    Never goes below 80%, even if 100% cloudy
    """
    
    pct_sun = 1 - get_cloudcover()
    pct_to_adj = 0.8 + 0.2*pct_sun
    adj_val = int(int(raw_val)*pct_to_adj)
    
    return adj_val

def update_leds():
    """Adjust LED based on whether sun is up and % cloudiness"""
    
    brightness = 0xffff if is_led_on else 0
    adjusted_brightness = mimic_clouds(brightness)
    
    led4.duty_cycle = adjusted_brightness

def func(vars):
    """Intersection of a line and a sphere

    Coordinate system centered on gnomon tip
    Line passes through gnomon tip and is in line with the sun
    Sphere is centered on the arm's pivot and has arm-length radius
    """
    
    alt, az, t = vars
    return [(arm["loc"][0] + arm["length"]*cos(alt)*cos(az-pi/2)) - (gnomon["loc"][0] + t*cos(gnomon["az"]-pi/2)),
            (arm["loc"][1] + arm["length"]*cos(alt)*sin(az-pi/2)) - (gnomon["loc"][1] + t*sin(gnomon["az"]-pi/2)),
            (arm["loc"][2] + arm["length"]*sin(alt)) - (gnomon["loc"][2] + t*tan(gnomon["alt"]))]

def validate_fsolve(x):
    """Ensure fsolve successfully found roots in the right quadrant"""
    
    finds_zeros = all(isclose(func(x), [0.0, 0.0, 0.0]))
    positive_t = x[2] >= 0

    return (finds_zeros and positive_t)

def rotate_angle(angle, min_val, max_val):
    """Adjust if our roots are the wrong multiple of 2pi

    e.g., sin(0) = sin(2pi) = sin(4pi) = ...
    """
    
    a = angle
    while a < min_val: a += 2*pi
    while a > max_val: a += -2*pi

    return a


# --- Setup Servo hat and assign LEDs and servos to their channels
i2c = I2C(SCL, SDA)
hat = PCA9685(i2c)
hat.frequency = 50

servo_alt = servo.Servo(hat.channels[13], min_pulse=600, max_pulse=2500)
servo_az = servo.Servo(hat.channels[15], min_pulse=600, max_pulse=2500)
led4 = hat.channels[4]

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
        
        # Light off and move servos
        is_led_on = False
        update_leds()
        
        servo_alt.angle = 135
        servo_az.angle = 90
        
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

            # Move servos and light on
            servo_alt.angle = (arm["alt"]+pi/2)*180/pi
            servo_az.angle = (arm["az"]-pi/2)*180/pi
            
            is_led_on = True
            update_leds()

            # Sleep 240 seconds (1 degree of earth's rotation)
            sleep(240)
        else:
            unstable_math = True

# Light off and servos to home position
is_led_on = False
update_leds()
servo_alt.angle = 135
servo_az.angle = 90
