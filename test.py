

from vehicle import JEEPNEY_PARAMS


mass = JEEPNEY_PARAMS["mass_empty"]
g = 9.81
Crr = JEEPNEY_PARAMS["Crr"]
rho = 1.225
Cd = JEEPNEY_PARAMS["Cd"]
A = JEEPNEY_PARAMS["frontal_area"]
v = 40/3.6


F_roll = mass * g * Crr

F_aero = (
    0.5
    * rho
    * Cd
    * A
    * v**2
)

F_resist = F_roll + F_aero
a_natural = F_resist / mass

print(a_natural)