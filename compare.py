import numpy as np
from datetime import datetime
from propagator import run, mu_earth, timestamps, rows
import matplotlib.pyplot as plt

# Compares propagated Artemis II trajectory against the OEM reference data.
# OEM timestamps are converted from UTC strings to seconds elapsed since TLI epoch
# for direct comparison with the propagator output.

epoch = datetime(2026, 4, 2, 23, 56, 22)
elapsed_seconds = [(datetime.strptime(t, "%Y-%m-%dT%H:%M:%S.%f") - epoch).total_seconds() for t in timestamps[349:]]

solution = run()
states_propagated = solution.sol(elapsed_seconds) #6xN

oem_states = np.array(rows[349:]) #Nx6

pro_position = states_propagated[0:3, :]
oem_position = oem_states[:, 0:3]

error = np.linalg.norm(pro_position - oem_position.T, axis=0)

elapsed_arr = np.array(elapsed_seconds)
mask = elapsed_arr <= 300000

print("max error up to 300,000 s (km):", error[mask].max())
print("mean error up to 300,000 s (km):", error[mask].mean())

idx = np.argmin(np.abs(elapsed_arr - 300000))
print("error at 300,000 s:", error[idx])

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(elapsed_seconds, error)
ax1.set_xlabel("seconds since epoch")
ax1.set_ylabel("position error (km)")
ax1.set_title("Propagator vs OEM")

oem_r = np.linalg.norm(oem_states[:, 0:3], axis=1)
oem_v = np.linalg.norm(oem_states[:, 3:6], axis=1)
oem_epsilon = (oem_v**2 / 2) - (mu_earth / oem_r)

ax2.plot(elapsed_seconds, oem_epsilon)
ax2.set_xlabel("seconds since epoch")
ax2.set_ylabel("specific orbital energy (km²/s²)")
ax2.set_title("OEM Specific Orbital Energy")


plt.figure()
plt.plot(elapsed_seconds[:-1], np.diff(oem_epsilon))
plt.xlabel("seconds since epoch")
plt.ylabel("step change in specific energy (km²/s²)")
plt.title("OEM energy jumps (spikes = burns)")

plt.tight_layout()
plt.show()