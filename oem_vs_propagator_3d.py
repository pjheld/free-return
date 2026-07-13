# oem_vs_propagator_3d.py
# Overlays OEM flight data and propagated trajectory in 3D inertial frame
# to see where and when Z components diverge

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from propagator import run, extract, timestamps, rows
from lunar_pos import skyview

# Load OEM data 
def parse_timestamp(ts):
    return datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")

datetimes = [parse_timestamp(ts) for ts in timestamps]

oem_positions = np.array([row[0:3] for row in rows])
oem_x = oem_positions[:, 0]
oem_y = oem_positions[:, 1]
oem_z = oem_positions[:, 2]

# Convert OEM datetimes to seconds from epoch
epoch = datetime(2026, 4, 2, 23, 56, 22)
oem_times = np.array([(dt - epoch).total_seconds() for dt in datetimes])

# Run propagator 
solution = run()
t_points = np.linspace(0, 8.8*24*3600, 2000)
states = solution.sol(t_points)

prop_x = states[0, :]
prop_y = states[1, :]
prop_z = states[2, :]

# 3D plot
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

ax.plot(oem_x, oem_y, oem_z, color='black', linewidth=1.5, label='OEM (actual)')
ax.plot(prop_x, prop_y, prop_z, color='cyan', linewidth=1.5, linestyle='--', label='Propagated')
ax.scatter(0, 0, 0, color='blue', s=100, label='Earth')

ax.set_xlabel('X (km)')
ax.set_ylabel('Y (km)')
ax.set_zlabel('Z (km)')
ax.set_title('OEM vs Propagated — Inertial Frame 3D')
ax.legend()

plt.tight_layout()
plt.savefig('oem_vs_propagator_3d.png', dpi=150, bbox_inches='tight')
plt.show()

