import numpy as np
from skyfield.api import load 
from datetime import datetime, timezone, timedelta

# Apollo 8 TLI conditions per "Boeing Postflight Trajectory AS-503, Table 3-V
# Range time: 10565.51 sec after launch (Dec 21 1968, 12:51:00 UTC)
# Altitude: 346.73 km
# Space-fixed velocity: 10822.05 m/s
# Flight path angle: 7.897 deg
# Heading angle: 67.494 deg
# Geodetic latitude: 21.477 deg N
# Longitude: -143.924 deg E

# convert to ECI X/Y/Z
alt_km = 346.73
lat_deg = 21.477
lon_deg = -143.924
speed_ms = 10822.05
speed = speed_ms/1000
fpa_deg = 7.897
hdg_deg = 67.494

# angles to rad
lat = np.deg2rad(lat_deg)
lon = np.deg2rad(lon_deg)
fpa = np.deg2rad(fpa_deg)
hdg = np.deg2rad(hdg_deg)
#hdg = np.deg2rad(-hdg_deg)

R_earth = 6371 # km / mean
r = R_earth + alt_km

X = r * np.cos(lat) * np.cos(lon)
Y = r * np.cos(lat) * np.sin(lon)
Z = r * np.sin(lat)

v_up = speed * np.sin(fpa)
v_north = speed * np.cos(fpa) * np.cos(hdg)
v_east = speed * np.cos(fpa) * np.sin(hdg)

# rotate into ECI
vx_ef = -v_north*np.sin(lat)*np.cos(lon) - v_east*np.sin(lon) + v_up*np.cos(lat)*np.cos(lon)
vy_ef = -v_north*np.sin(lat)*np.sin(lon) + v_east*np.cos(lon) + v_up*np.cos(lat)*np.sin(lon)
vz_ef =  v_north*np.cos(lat)                             + v_up*np.sin(lat)

ts=load.timescale()
launch_time = ts.utc(1968,12,21,12,51,0)
tli_time = ts.tt_jd(launch_time.tt + 10565.51 / 86400)
gst = tli_time.gast * np.pi / 12
tli_datetime = datetime(1968, 12, 21, 12, 51, 0, tzinfo=timezone.utc) + timedelta(seconds=10565.51)

x = X * np.cos(gst) - Y * np.sin(gst)
y = X * np.sin(gst) + Y * np.cos(gst)
z = Z
vx = vx_ef * np.cos(gst) - vy_ef * np.sin(gst)
vy = vx_ef * np.sin(gst) + vy_ef * np.cos(gst)
vz = vz_ef

state_apollo8 = np.array([x, y, z, vx, vy, vz])

# print(tli_datetime)


