from scipy.optimize import fsolve
import math

GNOMON_LOC = (0, 0, 0)
GNOMON_LENGTH = None
gnomon_alt = math.pi / 2
gnomon_az = math.pi / 2

ARM_LOC = (0, -2, 1)
ARM_LENGTH = 5
arm_alt = math.pi / 2
arm_az = math.pi / 2

def equations(vars):
    alt, az, t = vars
    return [ARM_LOC[0] + ARM_LENGTH*math.sin(alt) - (GNOMON_LOC[0] + t*math.tan(GNOMON_ALT)),
            ARM_LOC[1] + ARM_LENGTH*math.cos(alt)*math.sin(az) - (GNOMON_LOC[1] + t*math.sin(GNOMON_AZ)),
            ARM_LOC[2] + ARM_LENGTH*math.cos(alt)*math.cos(az) - (GNOMON_LOC[2] + t*math.cos(GNOMON_AZ))]

alt, az, t =  fsolve(equations, (math.pi / 2, math.pi / 2, 4))

print(equations((alt, az, t)))