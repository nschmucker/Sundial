import astropy.coordinates as coord
from astropy.time import Time
import astropy.units as u

# Independence Hall
# loc = coord.EarthLocation(lon=-75.15, lat=39.95)
# 
# now = Time.now()
# 
# altaz = coord.AltAz(location=loc, obstime=now)
# sun = coord.get_sun(now)
# 
# print(sun.transform_to(altaz))

now = Time('2021-03-06 10:00') #UTC time
# now = Time.now()
# loc = coord.EarthLocation.of_address('Philadelphia, PA')  # anything the google geocoding API resolves
# Independence Hall
loc = coord.EarthLocation(lon=-75.15*u.degree, lat=39.95*u.degree)
altaz = coord.AltAz(obstime=now, location=loc)

alt_ang = coord.get_sun(now).transform_to(altaz) # doesn't work. but below does

# import astropy.units as u
# from astropy.coordinates import SkyCoord
# from astropy.coordinates import FK5
# 
# gc = SkyCoord(l=0*u.degree, b=45*u.degree, frame='galactic')
# gc.transform_to('fk5')
# sc = SkyCoord(ra=1.0, dec=2.0, unit='deg', frame=FK5, equinox='J1980.0')
# gc.transform_to(sc)  