"""
helper_sundial_inputs.py
This file helps determine initial inputs for sundial.py

Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from pysolar.solar import get_altitude, get_azimuth
from scipy.optimize import fsolve
from numpy import isclose
from math import cos, sin, tan, pi
import datetime

GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
ARM_LOC = (0, -8, 6)
ARM_LENGTH = 13.25

# Independence Hall
LAT =  39.95
LON = -75.15

# Hawaii
# LAT =   19.8
# LON = -155.5

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
    "alt": 0.8,
    "az": 4,
    "t": 4.3
}
times = {
    "now": datetime.datetime.now(datetime.timezone.utc),
    "last_sunrise": None
}

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


# --- Determine time of "last_sunrise" ---
was_sun_up = get_altitude(LAT, LON, times["now"] + datetime.timedelta(minutes=-5)) > 0
is_sun_up = get_altitude(LAT, LON, times["now"]) > 0
while not (was_sun_up == False and is_sun_up == True):
    times["now"] += datetime.timedelta(minutes=1)
    was_sun_up = is_sun_up
    is_sun_up = get_altitude(LAT, LON, times["now"]) > 0
times["last_sunrise"] = times["now"] + datetime.timedelta(days=-1, minutes=-10)
times["now"] = datetime.datetime.now(datetime.timezone.utc)


# --- Determine the best fsolve guess for "last_sunrise" ---
gnomon["alt"] = get_altitude(LAT, LON, times["last_sunrise"])*pi/180
gnomon["az"] = get_azimuth(LAT, LON, times["last_sunrise"])*pi/180

root_ls = fsolve(func, (last_sunrise["alt"], last_sunrise["az"], last_sunrise["t"]))

# Validate fsolve worked and then correct our guess
if validate_fsolve(root_ls):
    # Move our alt and az to be in the correct range
    last_sunrise["alt"] = rotate_angle(root_ls[0], -pi/2, pi/2)
    last_sunrise["az"] = rotate_angle(root_ls[1], pi/2, 3*pi/2)
    last_sunrise["t"] = root_ls[2]
else:
    print("ERROR: Could not validate fsolve for 'last_sunrise'")
    print("")


# --- Determine the best fsolve guess for "now" ---
gnomon["alt"] = get_altitude(LAT, LON, times["now"])*pi/180
gnomon["az"] = get_azimuth(LAT, LON, times["now"])*pi/180
# Calculate sun's location relative to arm pivot point
root_g = fsolve(func, (guess["alt"], guess["az"], guess["t"]))

# Validate fsolve worked and then continue with updates
if validate_fsolve(root_g):
    # Move our alt and az to be in the correct range
    guess["alt"] = rotate_angle(root_g[0], -pi/2, pi/2)
    guess["az"] = rotate_angle(root_g[1], pi/2, 3*pi/2)
    guess["t"] = root_g[2]
else:
    print("ERROR: Could not validate fsolve for 'now' ('guess')")
    print("")

# --- Print outputs to be transferred into sundial.py ---
print("Set these variables:")
print("")
print("GNOMON_LOC = " + str(GNOMON_LOC))
print("GNOMON_LENGTH = " + str(GNOMON_LENGTH))
print("ARM_LOC = " + str(ARM_LOC))
print("ARM_LENGTH = " + str(ARM_LENGTH))
print("")
print("LAT = " + str(LAT))
print("LON = " + str(LON))
print("")
print("last_sunrise['alt']: " + str(round(last_sunrise['alt'], 1)))
print("last_sunrise['az']: " + str(round(last_sunrise['az'], 1)))
print("last_sunrise['t']: " + str(round(last_sunrise['t'], 1)))
print("")
print("guess['alt']: " + str(round(guess['alt'], 1)))
print("guess['az']: " + str(round(guess['az'], 1)))
print("guess['t']: " + str(round(guess['t'], 1)))
print("")
print("times['now']: Not hardcoded")
print("times['last_sunrise']: " + str(times['last_sunrise']))
