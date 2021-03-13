"""
sundial.py
This file contains code to run an indoor sundial
Developed on Python 3.7.3 / Raspberry Pi 4
Nathaniel Schmucker
"""

from icecream import ic # For debugging
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

class Viewer:
    """ This class is for all reference points for viewing the sun.
        loc and length must be the same units
        alt and az are in radians, relative to horizon and north """

    def __init__(self, loc, length, alt, az):
        self.loc = loc
        self.length = length
        self.alt = alt
        self.az = az

class Servo:
    """ This class is for all servos """

    def __init__(self, angle):
        self.angle = angle

    def update(self):
        ic(self.angle)

class LED:
    """ This class is for all LEDs """

    def __init__(self, brightness):
        self.brightness = brightness

    def update(self):
        ic(self.brightness)

def func(vars):
    alt, az, t = vars
    return [(arm.loc[0] + arm.length*cos(alt)*cos(az-pi/2)) - (gnomon.loc[0] + t*cos(gnomon.az-pi/2)),
            (arm.loc[1] + arm.length*cos(alt)*sin(az-pi/2)) - (gnomon.loc[1] + t*sin(gnomon.az-pi/2)),
            (arm.loc[2] + arm.length*sin(alt)) - (gnomon.loc[2] + t*tan(gnomon.alt))]

gnomon = Viewer(GNOMON_LOC, GNOMON_LENGTH, 0, 0)
arm = Viewer(ARM_LOC, ARM_LENGTH, 0, 0)
servo_alt = Servo(0)
servo_az = Servo(180)
led = LED(0xffff)

sunrise_time = datetime.datetime(2021, 3, 13, 11, 30, tzinfo=datetime.timezone.utc)
first_guess_alt = -0.1
first_guess_az = pi*3/4
first_guess_t = 4
sunrise_guess_alt = first_guess_alt
sunrise_guess_az = first_guess_az
sunrise_guess_t = first_guess_t
guess_alt = first_guess_alt
guess_az = first_guess_az
guess_t = first_guess_t

unstable_math = False
now = sunrise_time
while now < datetime.datetime(2021, 3, 15, 16, 30, tzinfo=datetime.timezone.utc) and not unstable_math:
    sleep(0.5)
#     now = datetime.datetime.now(datetime.timezone.utc)
    
    # Get sun's location at current time (in radians)
    gnomon.alt = get_altitude(LAT, LON, now)*pi/180
    gnomon.az = get_azimuth(LAT, LON, now)*pi/180
    
    ic(now)
    ic(gnomon.alt*180/pi)
    ic(gnomon.az*180/pi)
    
    if gnomon.alt < 0:
        # Prep our next guess to be the last sunrise alt/az/t
        guess_alt = sunrise_guess_alt
        guess_az = sunrise_guess_az
        guess_t = sunrise_guess_t
        
        # light off and servos to home position
        led.brightness = 0
        servo_alt.angle = 135
        servo_az.angle = 90
        
        ic(sunrise_time)
        ic(first_guess_alt*180/pi)
        ic(first_guess_az*180/pi)
        ic(first_guess_t)
        ic(sunrise_guess_alt*180/pi)
        ic(sunrise_guess_az*180/pi)
        ic(sunrise_guess_t)
        ic(guess_alt*180/pi)
        ic(guess_az*180/pi)
        ic(guess_t)
        ic(arm.alt)
        ic(arm.az)
        
        # Update the physical sundial
        led.update()
        servo_alt.update()
        servo_az.update()
        
        # Sleep until 10 minutes before this morning's sunrise
        sleep_time = sunrise_time + datetime.timedelta(days=1, minutes=-10) - now
#         sleep(int(sleep_time))
        ic(sleep_time)
        print("")
        now += sleep_time
        
    else:
        # Calculate sun's location relative to arm pivot point
        root = fsolve(func, (guess_alt, guess_az, guess_t))
        
        ic(root)
        ic(isclose(func(root), [0.0, 0.0, 0.0]))

        if not all(isclose(func(root), [0.0, 0.0, 0.0])):
            unstable_math = True
        else:           
            arm.alt = root[0]
            arm.az = root[1] + pi if root[1] < 0 else root[1]
            # TODO: Better quadrant validation
            
            # Refresh our best guess for sunrise alt/az/t
            if led.brightness == 0:
                sunrise_time = now
                sunrise_guess_alt = arm.alt
                sunrise_guess_az = arm.az
                sunrise_guess_t = root[2]
            
            # Prep our next guess to be the latest solution
            guess_alt = arm.alt
            guess_az = arm.az
            guess_t = root[2]
            
            led.brightness = 0xffff
            servo_alt.angle = (pi/2+arm.alt)*180/pi
            servo_az.angle = (arm.az-pi/2)*180/pi
            
            ic(sunrise_time)
            ic(sunrise_guess_alt*180/pi)
            ic(sunrise_guess_az*180/pi)
            ic(sunrise_guess_t)
            ic(guess_alt*180/pi)
            ic(guess_az*180/pi)
            ic(guess_t)
            ic(arm.alt)
            ic(arm.az)
            
            # Update the physical sundial
            servo_alt.update()
            servo_az.update()
            led.update()

            # Sleep 10 minutes
            # TODO: What is the resolution of the servos?
#             sleep(60*10)
            print("Sleep: 10 min")
            print("")
            now += datetime.timedelta(minutes=90)

# light off and servos to home position
led.brightness = 0
servo_alt.angle = 135
servo_az.angle = 90

# Update the physical sundial
led.update()
servo_alt.update()
servo_az.update()

print("Variables upon abort:")
