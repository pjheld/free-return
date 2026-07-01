# Returns geocentric Moon position (km) at a given UTC time using JPL DE421 ephemeris
import numpy as np
from skyfield.api import load

eph = load('de421.bsp')
ts = load.timescale()

def skyview(year, month, day, hour, minute, second):
    earth, moon = eph['earth'], eph['moon']
    t = ts.utc(year, month, day, hour, minute, second)
    moon_pos = (moon - earth).at(t).position.km  # geocentric Moon position in km
    return moon_pos