from pysolar.solar import *
import datetime

latitude = 42.206
longitude = -71.382
date = datetime.datetime.now(datetime.timezone.utc)
print(get_altitude(latitude, longitude, date))
print(get_azimuth(latitude, longitude, date))