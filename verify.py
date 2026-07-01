import numpy as np
import matplotlib.pyplot as plt
from propagator import run, mu_earth

solution = run(two_body=True)
r = solution.y[0:3,:]
v = solution.y[3:6,:]

r_norm = np.linalg.norm(solution.y[0:3,:], axis = 0)
v_norm = np.linalg.norm(solution.y[3:6,:], axis = 0)

## Specific Orbital Energy should remain Constant----------------------------------------------------
epsilon = (v_norm**2 / 2) - (mu_earth / r_norm)

print("min energy:", epsilon.min(), "max energy: ", epsilon.max())
print("epsilon drift: ", epsilon.max() - epsilon.min()) 
# Energy is conserved to 1 part in 56 million over 10 days. Plot shows noise floor, not signal. 

#plt.plot(solution.t,epsilon)
#plt.show()

## Angular Momentum Magnitude -----------------------------------------------------------------------
# how much rotational motion does the s/c have around Earth. For 2-body = constant
angular_momentum = np.cross(r,v, axisa=0, axisb=0)
angular_momentum_norm = np.linalg.norm(angular_momentum, axis = 1)

print("min h: ",angular_momentum_norm.min(), "max h: ", angular_momentum_norm.max())
print("h drift: ", angular_momentum_norm.max()-angular_momentum_norm.min())
# Ang Mom conserved to 1 part in 1.6 billion

## Kepler Period -------------------------------------------------------------------------------------
v_circ = np.sqrt(mu_earth / 8000)
state_0_circ = [8000, 0, 0, 0, v_circ, 0]
T_kepler = 2 * np.pi * np.sqrt(8000**3/mu_earth)
solution_circ = run(two_body=True, t_span=(0,T_kepler*1.1), state_0 = state_0_circ)

y_circ = solution_circ.y[1,:]
sign_changes = np.where(np.diff(np.sign(y_circ)))[0]
T_numerical = solution_circ.t[sign_changes[2]]
print("T_kepler: " , T_kepler)
print("T_numerical: ", T_numerical)
print("error %: ", abs(T_numerical - T_kepler) / T_kepler*100)
# 0.059% error. acceptable for numerical integrator
# My point-mass gravity model matches the real Artemis II trajectory to within 3,790 km through the first 4 days of ballistic flight, after which error grows due to a trajectory correction burn that my model doesn't account for.
# A simple two-force model - Earth and the moon's gravity - reproduces a real lunar mission trajectory to within 3,790 kilometers using publicly avaiable flight data. The limitation is known