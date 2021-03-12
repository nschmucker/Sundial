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

def func(vars):
    alt, az, t = vars
    return [(ARM_LOC[0] + ARM_LENGTH*math.cos(alt)*math.cos(az)) - (GNOMON_LOC[0] + t*math.cos(gnomon_az)),
            (ARM_LOC[1] + ARM_LENGTH*math.cos(alt)*math.sin(az)) - (GNOMON_LOC[1] + t*math.sin(gnomon_az)),
            (ARM_LOC[2] + ARM_LENGTH*math.sin(alt)) - (GNOMON_LOC[2] + t*math.tan(gnomon_alt))]

unstable_math = False
while not unstable_math:

    now = datetime.datetime.now(datetime.timezone.utc) #TODO: Adjust for Eastern Time/DST
    
    # Get sun's location at current time
    gnomon_alt = get_altitude(LAT, LON, now)
    gnomon_az = get_azimuth(LAT, LON, now)
    
    if gnomon_alt < 0:
        # light off
        # servos to home position
        # sleep XX hours
    else:
        # Calculate sun's location relative to arm pivot point
        root = fsolve(func, (math.pi / 3, math.pi / 2, 8))
        
        if not all(isclose(func(root), [0.0, 0.0, 0.0])):
            unstable_math = True
        else:           
            arm_alt = root[0]
            arm_az = root[1] + math.pi if root[1] < 0 else root[1]
            
            # servos to XX position,
            # light on
            # sleep at least as long as resolution of Servos

# light off
# servos to home position
