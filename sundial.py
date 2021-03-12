"""
sundial.py
This file contains code to run an indoor sundial
Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from pysolar.solar import get_altitude, get_azimuth
from scipy.optimize import fsolve
from numpy import isclose
import datetime
import math

GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
ARM_LOC = (0, -2, 1)
ARM_LENGTH = 5

# Independence Hall
LAT =  39.95
LON = -75.15

class Viewer:
    """ This class is for all reference points for viewing the sun """

    def __init__(self, loc, length, alt. az):
        self.loc = loc
        self.length = length
        self.alt = alt
        self.az = az

class Servo:
    """ This class is for all servos """

    def __init__(self, angle):
        self.angle = angle

    def update(self):
        return

class LED:
    """ This class is for all LEDs """

    def __init__(self, brightness):
        self.brightness = brightness

    def update(self):
        return

#TODO: Rework to have azimuth relative to North
def func(vars):
    alt, az, t = vars
    return [(arm.loc[0] + arm.length*math.cos(alt)*math.cos(az)) - (gnomon.loc[0] + t*math.cos(gnomon.az)),
            (arm.loc[1] + arm.length*math.cos(alt)*math.sin(az)) - (gnomon.loc[1] + t*math.sin(gnomon.az)),
            (arm.loc[2] + arm.length*math.sin(alt)) - (gnomon.loc[2] + t*math.tan(gnomon.alt))]

gnomon = Viewer(GNOMON_LOC, GNOMON_LENGTH, 0, 0)
arm = Viewer(ARM_LOC, ARM_LENGTH, 0, 0)
servo_alt = Servo(0)
sevro_az = Servo(180)
led = Led(0)

unstable_math = False
while not unstable_math:

    now = datetime.datetime.now(datetime.timezone.utc) #TODO: Adjust for Eastern Time/DST
    
    # Get sun's location at current time
    gnomon.alt = get_altitude(LAT, LON, now)
    gnomon.az = get_azimuth(LAT, LON, now)
    
    if gnomon.alt < 0:
        # light off
        # servos to home position
        # led.brightness = off
        # servo_alt.angle = 
        # servo_az.angle = 

        led.update
        servo_alt.update
        servo_az.update
        
        # sleep until sunrise
    else:
        # Calculate sun's location relative to arm pivot point
        # TODO: Better guesser
        root = fsolve(func, (math.pi / 3, math.pi / 2, 8))

        if not all(isclose(func(root), [0.0, 0.0, 0.0])):
            unstable_math = True
        else:           
            arm.alt = root[0]*180/math.pi
            arm.az = root[1]*180/math.pi + 180 if root[1] < 0 else root[1]*180/math.pi
            # TODO: Better quadrant validation
            # led.brightness = on
            # servo_alt.angle = 
            # servo_az.angle = 

            servo_alt.update
            servo_az.update
            led.update

            # sleep at least as long as resolution of Servos

# light off
# servos to home position

led.update
servo_alt.update
servo_az.update
