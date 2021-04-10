from scipy.optimize import fsolve
from numpy import isclose
import math

GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
gnomon_alt = math.pi / 2
gnomon_az = math.pi / 2

ARM_LOC = (0, -2, 1)
ARM_LENGTH = 6
arm_alt = math.pi / 2
arm_az = math.pi / 2

def func(vars):
    alt, az, t = vars
    return [(ARM_LOC[0] + ARM_LENGTH*math.cos(alt)*math.cos(az)) - (GNOMON_LOC[0] + t*math.cos(gnomon_az)),
            (ARM_LOC[1] + ARM_LENGTH*math.cos(alt)*math.sin(az)) - (GNOMON_LOC[1] + t*math.sin(gnomon_az)),
            (ARM_LOC[2] + ARM_LENGTH*math.sin(alt)) - (GNOMON_LOC[2] + t*math.tan(gnomon_alt))]

root = fsolve(func, (math.pi / 3, math.pi / 2, 8))

# My values
print(root)

# Should equal 0
print(func(root))
print(isclose(func(root), [0.0, 0.0, 0.0]))
