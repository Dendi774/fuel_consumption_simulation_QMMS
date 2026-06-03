

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


def calculate_natural_deceleration(speed):
    """
    Deceleration when driver lifts off throttle — no engine, no brakes.
    Only rolling resistance and aerodynamic drag act on the vehicle.
    These come directly from the resistive terms of Equation 1 (with a=0).

    a_natural = -(F_rolling + F_aero) / mass
    """
    F_rolling = JEEPNEY_PARAMS["mass_empty"] * g * JEEPNEY_PARAMS["Crr"]
    F_aero    = (0.5 * rho
                 * JEEPNEY_PARAMS["Cd"]
                 * JEEPNEY_PARAMS["frontal_area"]
                 * speed ** 2)
    return -(F_rolling + F_aero) / JEEPNEY_PARAMS["mass_empty"]



print(calculate_natural_deceleration(v))
