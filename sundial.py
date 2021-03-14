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
from time import sleep
import datetime

GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
ARM_LOC = (0, -2, 1)
ARM_LENGTH = 5

# Independence Hall
LAT =  39.95
LON = -75.15

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
servo_alt = Servo(0)
servo_az = Servo(180)
led = LED(0xffff)

sunrise_time = datetime.datetime(2021, 3, 13, 11, 30, tzinfo=datetime.timezone.utc)
sunrise_guess_alt = -0.1
sunrise_guess_az = pi*3/4
sunrise_guess_t = 4
first_guess_alt = 0.3
first_guess_az = 3.5
first_guess_t = 3
guess_alt = first_guess_alt
guess_az = first_guess_az
guess_t = first_guess_t

unstable_math = False
while not unstable_math:
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # Get sun's location at current time (in radians)
    gnomon["alt"] = get_altitude(LAT, LON, now)*pi/180
    gnomon["az"] = get_azimuth(LAT, LON, now)*pi/180
    
    if gnomon["alt"] < 0:
        # Sleep until 10 minutes before this morning's sunrise
        #  and then increments of 1 minute until sunrise
        if led.brightness > 0:
            sleep_time = sunrise_time + datetime.timedelta(days=1, minutes=-10) - now
        else:
            sleep_time = datetime.timedelta(minutes=1)
        
        # Prep our next guess to be the last sunrise alt/az/t
        guess_alt = sunrise_guess_alt
        guess_az = sunrise_guess_az
        guess_t = sunrise_guess_t
        
        # light off and servos to home position
        led.brightness = 0
        servo_alt.angle = 135
        servo_az.angle = 90
        
        # Update the physical sundial
        led.update()
        servo_alt.update()
        servo_az.update()
        
        sleep(int(sleep_time))
        
    else:
        # Calculate sun's location relative to arm pivot point
        root = fsolve(func, (guess_alt, guess_az, guess_t))

        # Validate fsolve worked and then continue with updates
        if not all(isclose(func(root), [0.0, 0.0, 0.0])):
            unstable_math = True
        elif root[2] < 0:
            unstable_math = True
        else:
            # alt in range: [-pi/2, pi/2]
            arm["alt"] = root[0]
            while arm["alt"] < -pi/2: arm["alt"] += 2*pi
            while arm["alt"] > pi/2: arm["alt"] += -2*pi
            
            # az in range: [pi/2, 3*pi/2]
            arm["az"] = root[1]
            while arm["az"] < pi/2: arm["az"] += 2*pi
            while arm["az"] > 3*pi/2: arm["az"] += -2*pi
            
            # If the sun is coming up, refresh our best guess for sunrise time/alt/az/t
            if led.brightness == 0:
                sunrise_time = now
                sunrise_guess_alt = arm["alt"]
                sunrise_guess_az = arm["az"]
                sunrise_guess_t = root[2]
            
            # Prep our next guess to be the latest solution
            guess_alt = arm["alt"]
            guess_az = arm["az"]
            guess_t = root[2]
            
            led.brightness = 0xffff
            servo_alt.angle = (arm["alt"]+pi/2)*180/pi
            servo_az.angle = (arm["az"]-pi/2)*180/pi
                        
            # Update the physical sundial
            servo_alt.update()
            servo_az.update()
            led.update()

            # Sleep 10 minutes
            sleep(60*10) # TODO: What is the resolution of the servos?

# light off and servos to home position
led.brightness = 0
servo_alt.angle = 135
servo_az.angle = 90

# Update the physical sundial
led.update()
servo_alt.update()
servo_az.update()
