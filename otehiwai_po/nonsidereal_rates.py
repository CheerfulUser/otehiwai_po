from astroquery.jplhorizons import Horizons
import datetime 
from datetime import timezone
from astropy.time import Time
from astropy.coordinates import SkyCoord
from astropy import units as u 
# name of comet as input

def horizons(name):
    dt = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    epoch = Time(dt)
    obj = Horizons(id=name, location='474', epochs=epoch.jd)
    print('checking ephemerides for %s at %s' %(name, dt))
    e = obj.ephemerides()
    ra = e['RA'].value.data[0] # convert RA to HHMMSS
    dec = e['DEC'].value.data[0]
    coords = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
    coords = coords.to_string('hmsdms', sep=':')
    RArate = e['RA_rate'].value.data[0] / 3600
    DECrate = e['DEC_rate'].value.data[0] / 3600
    print("Coordinates: %s, RA rate: %s, Dec rate: %s" %(coords, str(round(RArate,4)), str(round(DECrate,4))))

name = input("Enter target: ")
horizons(name)