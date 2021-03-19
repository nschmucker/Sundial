# Sundial
Build an sunless sundial with Raspberry Pi

## Setup notes
 * Running latest Raspbian image (Buster)
 * Update system using `sudo apt-get update && sudo apt-get upgrade` (30+ mins)
 * Install extra packages using `sudo apt install python3-scipy`
 * Install extra packages using `sudo pip3 install pysolar adafruit-circuitpython-servokit`
 * Running Pi 4 with Adafruit 16-servo
   * Turn on I2C: `sudo raspi-config` > "Interfacing Options" > I2C > Enable
   * Then: `sudo reboot`
   * Then test the hat is being found with: `sudo i2cdetect -y 1`