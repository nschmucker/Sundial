import astropy.units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz, get_sun

utcoffset = -4*u.hour  # Eastern Daylight Time
time = Time('2012-7-12 23:00:00') - utcoffset

sun = get_sun(time)
print("sun:")
print(sun)

m33 = SkyCoord.from_name('M33')
print("m33:")
print(m33)

bear_mountain = EarthLocation(lat=41.3*u.deg, lon=-74*u.deg)
print("bm:")
print(bear_mountain)

aa = AltAz(obstime=time,location=bear_mountain)
print("aa:")
print(aa)

m33altaz = m33.transform_to(frame = aa, merge_attributes=False)
print("M33's Altitude = {0.alt:.2}".format(m33altaz))

sunaltaz = sun.transform_to(frame = aa)
print("Sun's Altitude = {0.alt:.2}".format(sunaltaz))