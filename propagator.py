import numpy as np
import matplotlib.pyplot as plt
from lunar_pos import skyview 
from datetime import datetime
from datetime import timedelta
from scipy.integrate import solve_ivp
from apollo8_state import state_apollo8, tli_time, tli_datetime

mu_earth = 398600.4355   
mu_moon = 4902.8001
epoch = datetime(2026,  4, 2, 23, 56, 22)

# Parser
def extract(filename):

    timestamps = []
    rows = []
    with open(filename) as f:
        for line in f:
            if line[:1].isdigit():
                parts = line.split()
                timestamps.append(parts[0])
                rows.append([float(x) for x in line.split()[1:]])
            
    return timestamps, rows
timestamps, rows = extract("Artemis_II_OEM_2026_04_04_to_EI.asc")
state_0 = rows[349]

# Integrator
def run(two_body=False, t_span = (0, 10*24*60*60), state_0 = None, epoch=datetime(2026, 4, 2, 23, 56, 22), max_step=np.inf):
    
    if state_0 is None:
        state_0 = rows[349]
    def ode(t, state):
        t_current = epoch + timedelta(seconds=t)
   
        r = state[0:3]
        v = state[3:6]
        # Calculate acceleration
        a_earth = -mu_earth * (r) / np.linalg.norm(r)**3
        
        if two_body:
            a_total = a_earth
        else:
            moon_position = skyview(t_current.year, t_current.month, t_current.day, t_current.hour, t_current.minute, t_current.second)
            a_moon = mu_moon * (moon_position - r) / np.linalg.norm(moon_position - r)**3
            a_total = a_earth + a_moon
        
        return np.concatenate([v, a_total])
    
    solution = solve_ivp(ode, t_span, state_0, 'RK45', dense_output=True, rtol=1e-9, atol=1e-12, max_step=max_step)
    return solution

if __name__ == "__main__":
    solution_artemis = run()
    solution_apollo8 = run(state_0=state_apollo8, t_span=(0, 259200), epoch=tli_datetime, max_step=500)
    moon_times_check = solution_apollo8.t
    min_moon_dist = np.inf
    for t in moon_times_check:
        t_current = tli_datetime + timedelta(seconds=t)
        mp = skyview(t_current.year, t_current.month, t_current.day, t_current.hour, t_current.minute, t_current.second)
        dist = np.linalg.norm(solution_apollo8.sol(t)[:3] - mp)
        if dist < min_moon_dist:
            min_moon_dist = dist
    print("Closest Moon approach:", min_moon_dist, "km")


    # Extract trajectories    
    art_x = solution_artemis.y[0, :]
    art_y = solution_artemis.y[1, :]
    art_z = solution_artemis.y[2, :]

    ap8_x = solution_apollo8.y[0, :]
    ap8_y = solution_apollo8.y[1, :]
    ap8_z = solution_apollo8.y[2, :]

    # Moon path for Artemis II
    artemis_epoch = datetime(2026, 4, 2, 23, 56, 22)
    moon_times_artemis = np.linspace(0, 10*24*60*60, 200)
    moon_artemis = [skyview(*(artemis_epoch + timedelta(seconds=t)).timetuple()[:6]) for t in moon_times_artemis]
    moon_artemis = np.array(moon_artemis)

    # Moon path for Apollo 8 
    moon_times_apollo8 = np.linspace(0, 259200, 200)
    moon_apollo8 = [skyview(*(tli_datetime + timedelta(seconds=t)).timetuple()[:6]) for t in moon_times_apollo8]
    moon_apollo8 = np.array(moon_apollo8)

    # Plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(art_x, art_y, art_z, color='cyan', label='Artemis II')
    ax.plot(ap8_x, ap8_y, ap8_z, color='orange', label='Apollo 8')

    ax.scatter(0, 0, 0, color='blue', s=100, label='Earth')

    ax.plot(moon_artemis[:, 0], moon_artemis[:, 1], moon_artemis[:, 2], 
            color='cyan', linestyle='--', alpha=0.4, label='Moon (Artemis)')
    ax.plot(moon_apollo8[:, 0], moon_apollo8[:, 1], moon_apollo8[:, 2], 
            color='orange', linestyle='--', alpha=0.4, label='Moon (Apollo 8)')

    # Axis scaling 
    all_x = np.concatenate([art_x, ap8_x, moon_artemis[:, 0], moon_apollo8[:, 0]])
    all_y = np.concatenate([art_y, ap8_y, moon_artemis[:, 1], moon_apollo8[:, 1]])
    all_z = np.concatenate([art_z, ap8_z, moon_artemis[:, 2], moon_apollo8[:, 2]])

    max_range = np.array([all_x.max()-all_x.min(),
                          all_y.max()-all_y.min(),
                          all_z.max()-all_z.min()]).max() / 2

    mid_x = (all_x.max()+all_x.min()) / 2
    mid_y = (all_y.max()+all_y.min()) / 2
    mid_z = (all_z.max()+all_z.min()) / 2

    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)
    ax.set_box_aspect([1,1,1])

    ax.set_xlabel('X (km)')
    ax.set_ylabel('Y (km)')
    ax.set_zlabel('Z (km)')
    ax.set_title('Apollo 8 vs Artemis II — Free Return Trajectories')
    ax.legend()

    plt.show()