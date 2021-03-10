"""
sundial.py
This file contains code to run an indoor sundial
Developed on Python 2.7.16 / Raspberry Pi 4
Nathaniel Schmucker
"""

from scipy.optimize import fsolve
import math

def equations(p):
    x, y = p
    return (x+y**2-4, math.exp(x) + x*y - 3)

x, y =  fsolve(equations, (1, 1))

print equations((x, y))

# --- Global constants ---
GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
ARM_LOC = (0, -2, 1)
ARM_LENGTH = 5

def equations(vars):
    alt, az, t = vars
    return [ARM_LOC[0] + ARM_LENGTH*math.sin(alt) - (GNOMON_LOC[0] + t*math.tan(GNOMON_ALT)),
            ARM_LOC[1] + ARM_LENGTH*math.cos(alt)*math.sin(az) - (GNOMON_LOC[1] + t*math.sin(GNOMON_AZ)),
            ARM_LOC[2] + ARM_LENGTH*math.cos(alt)*math.cos(az) - (GNOMON_LOC[2] + t*math.cos(GNOMON_AZ))]

gnomon_alt = math.pi / 2
gnomon_az = math.pi / 2
arm_alt = math.pi / 2
arm_az = math.pi / 2

alt, az, t =  fsolve(equations, (math.pi / 2, math.pi / 2, 4))

while True:

    # Get sun's new location
    gnomon_alt =
    gnomon_az =
    
    # Calculate sun's location relative to arm pivot point
    arm_altaz =
    
    arm.alt =
    arm.az =
    
    # Update object positions
    game.run_logic()

    # Draw the current frame
    game.display_frame(screen, font)

    # Limit to 60 frames per second
    clock.tick(60)
