"""
sundial.py
This file contains code to test sundial.py
Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from icecream import ic
from pysolar.solar import get_altitude, get_azimuth
from scipy.optimize import fsolve
from numpy import isclose
from math import cos, sin, tan, pi
from time import sleep
import datetime

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
    "last_sunrise": datetime.datetime(2021, 3, 14, 11, 20, tzinfo=datetime.timezone.utc)
}

class Servo:
    """ This class is for all servos
        angle in range [0, 180] (degrees) """

    def __init__(self, angle):
        self.angle = angle

    def update(self):
        print(str(self.angle))

class LED:
    """ This class is for all LEDs
        brightness in range [0, 0xffff] (16-bit value) """

    def __init__(self, brightness):
        self.brightness = brightness

    def update(self):
        print(str(self.brightness))

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
led = LED(0xffff)

unstable_math = False
i = 0
while (not unstable_math and i < 20):    
    i += 1
    
    ic(gnomon)
    ic(arm)
    ic(times)
    ic(last_sunrise)
    ic(guess)
    
    # Get sun's location at current time (in radians)
    gnomon["alt"] = get_altitude(LAT, LON, times["now"])*pi/180
    gnomon["az"] = get_azimuth(LAT, LON, times["now"])*pi/180
    
    if gnomon["alt"] < 0:
        # Sleep until 10 minutes before this morning's sunrise
        #  and then increments of 1 minute until sunrise
        if led.brightness > 0:
            sleep_time = times["last_sunrise"] + datetime.timedelta(days=1, minutes=-10) - times["now"]
        else:
            sleep_time = datetime.timedelta(minutes=1)
        
        # Prep our next guess to be the last sunrise alt/az/t
        guess["alt"] = last_sunrise["alt"]
        guess["az"] = last_sunrise["az"]
        guess["t"] = last_sunrise["t"]
        
        # Light off and servos to home position
        led.brightness = 0
        servo_alt.angle = 135
        servo_az.angle = 90
        
        # Update the physical sundial
        led.update()
        servo_alt.update()
        servo_az.update()
        
        times["now"] += sleep_time
        
    else:
        # Calculate sun's location relative to arm pivot point
        root = fsolve(func, (guess["alt"], guess["az"], guess["t"]))

        # Validate fsolve worked and then continue with updates
        if validate_fsolve(root):
            # Move our alt and az to be in the correct range
            arm["alt"] = rotate_angle(root[0], -pi/2, pi/2)
            arm["az"] = rotate_angle(root[1], pi/2, 3*pi/2)
            
            # If the sun is coming up, refresh our best guess for sunrise time/alt/az/t
            if led.brightness == 0:
                times["last_sunrise"] = times["now"]
                last_sunrise["alt"] = arm["alt"]
                last_sunrise["az"] = arm["az"]
                last_sunrise["t"] = root[2]
            
            # Prep our next guess to be the latest solution
            guess["alt"] = arm["alt"]
            guess["az"] = arm["az"]
            guess["t"] = root[2]

            # Light on and servos to appropriate position
            led.brightness = 0xffff
            servo_alt.angle = (arm["alt"]+pi/2)*180/pi
            servo_az.angle = (arm["az"]-pi/2)*180/pi
                        
            # Update the physical sundial
            servo_alt.update()
            servo_az.update()
            led.update()

            # Sleep 10 minutes
            times["now"] += datetime.timedelta(minutes = 10)
            
        else:
            unstable_math = True

# Light off and servos to home position
led.brightness = 0
servo_alt.angle = 135
servo_az.angle = 90

# Update the physical sundial
led.update()
servo_alt.update()
servo_az.update()

if unstable_math: print("Reached unstable_math == True")