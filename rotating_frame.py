# Run Artemis II propagation to get states over 10 days
# At each timestep, get the Moon's position
# Compute the angle the Moon makes with the x-axis at each timestep
# Apply 2D rotation matrix to s/c and Moon's position to freeze the Moon's orbital motion on the x-axis
# Plot the Result

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from propagator import run
from lunar_pos import skyview
from apollo8_state import state_apollo8, tli_datetime

# Run Artemis II propagation
epoch = datetime(2026, 4, 2, 23, 56, 22)
solution = run()

# Sample trajectory at evenly spaced points
t_points = np.linspace(0, 8.5 * 24 * 3600, 1000)
states = solution.sol(t_points)
sc_x = states[0,:]
sc_y = states[1,:]

# Moon's position at timesteps
moon_positions = []
for t in t_points:
    t_current = epoch + timedelta(seconds=t)
    moon_pos = skyview(t_current.year, t_current.month, t_current.day, t_current.hour, t_current.minute, t_current.second)
    moon_positions.append(moon_pos)

moon_positions = np.array(moon_positions)
moon_x = moon_positions[:, 0]
moon_y = moon_positions[:, 1]

# Rotation at each timestep
theta = np.arctan2(moon_y, moon_x)
# rotation matrix to s/c position each timestep
sc_x_rot = sc_x * np.cos(-theta) - sc_y * np.sin(-theta)
sc_y_rot = sc_x * np.sin(-theta) + sc_y * np.cos(-theta)
# same thing for moon position
moon_x_rot = moon_x * np.cos(-theta) - moon_y * np.sin(-theta)
moon_y_rot = moon_x * np.sin(-theta) + moon_y * np.cos(-theta)


# Run Apollo 8 Propagation

solution_ap8 = run(state_0=state_apollo8, t_span = (0,3*24*3600), epoch = tli_datetime, max_step=500)
t_points_ap8 = np.linspace(0, 3 * 24 * 3600, 1000)
states_ap8 = solution_ap8.sol(t_points_ap8)
sc_x_ap8 = states_ap8[0,:]
sc_y_ap8 = states_ap8[1,:]

# Get Moon position at each timestep
moon_positions_ap8 = []
for t in t_points_ap8:
    t_current = tli_datetime + timedelta(seconds=t)
    moon_pos = skyview(t_current.year, t_current.month, t_current.day, t_current.hour, t_current.minute, t_current.second)
    moon_positions_ap8.append(moon_pos)

moon_positions_ap8 = np.array(moon_positions_ap8)
moon_x_ap8 = moon_positions_ap8[:, 0]
moon_y_ap8 = moon_positions_ap8[:, 1]

# Rotate Apollo 8 into rotating frame
theta_ap8 = np.arctan2(moon_y_ap8, moon_x_ap8)
sc_x_ap8_rot = sc_x_ap8 * np.cos(-theta_ap8) - sc_y_ap8 * np.sin(-theta_ap8)
sc_y_ap8_rot = sc_x_ap8 * np.sin(-theta_ap8) + sc_y_ap8 * np.cos(-theta_ap8)




# Plotting 
fig, ax = plt.subplots(figsize=(10, 8))

ax.plot(sc_x_rot, sc_y_rot, color='cyan', linewidth=1.5, label='Artemis II (rotating frame)')
ax.plot(sc_x_ap8_rot, sc_y_ap8_rot, color='orange', linewidth=1.5, label='Apollo 8 (rotating frame)')

ax.scatter(0, 0, color='blue', s=150, zorder=5, label='Earth')
ax.scatter(moon_x_rot.mean(), 0, color='gray', s=100, zorder=5, label='Moon (fixed)')

# Direction arrow - Artemis II
ax.annotate('', xy=(sc_x_rot[220], sc_y_rot[220]),
            xytext=(sc_x_rot[200], sc_y_rot[200]),
            arrowprops=dict(arrowstyle='->', color='cyan', lw=2))

# Direction arrow - Apollo 8
ax.annotate('', xy=(sc_x_ap8_rot[220], sc_y_ap8_rot[220]),
            xytext=(sc_x_ap8_rot[200], sc_y_ap8_rot[200]),
            arrowprops=dict(arrowstyle='->', color='orange', lw=2))

ax.set_xlabel('X rotating (km)')
ax.set_ylabel('Y rotating (km)')
ax.set_title('Apollo 8 vs Artemis II — Earth-Moon Rotating Frame')
ax.legend()
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('rotating_frame.png', dpi=150, bbox_inches='tight')
plt.show()

