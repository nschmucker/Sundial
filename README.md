# Sundial
Build a sunless sundial with Raspberry Pi

## Setup notes
 * Running Pi 4 with latest Raspbian image (Buster)
 * Update system using `sudo apt-get update && sudo apt-get upgrade` (30+ mins)
 * Install extra packages using `sudo apt install python3-scipy`
 * Install extra packages using `sudo pip3 install pysolar adafruit-circuitpython-adafruit_pca9685 adafruit-circuitpython-adafruit_motor`
 * Connect Adafruit 16-servo hat
   * Turn on I2C: `sudo raspi-config` > "Interfacing Options" > I2C > Enable
   * Then: `sudo reboot`
   * Then test the hat is being found with: `sudo i2cdetect -y 1`