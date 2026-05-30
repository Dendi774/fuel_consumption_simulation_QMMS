import numpy as np
import pandas as pd
from vehicle import JEEPNEY_PARAMS
from routes import ROUTES
from behaviors import BEHAVIOR_PROFILES

# Physical constants
RHO_AIR = 1.225   # kg/m³ — air density at sea level (ISO 2533)
GRAVITY = 9.81    # m/s²  — gravitational acceleration
DT      = 1.0     # s     — simulation timestep (1 second)
ETA = JEEPNEY_PARAMS["eta_mt"] * 0.35


def calculate_traction_force(v, a, mass, Cd, frontal_area, Crr):
    """
    Equation 1 from Zacharof et al. (2024)
    Calculates the traction force the engine must produce.

    F_traction = (m × a) + (m × g × Crr) + (½ × ρ × Cd × A × v²)

    Parameters:
        v             — current speed in m/s
        a             — current acceleration in m/s² (positive = speeding up)
        mass          — vehicle mass in kg
        Cd            — drag coefficient (dimensionless)
        frontal_area  — frontal area in m²
        Crr           — rolling resistance coefficient (dimensionless)

    Returns:
        F_traction    — total force in Newtons (N)
        F_inertia     — inertial component (m × a)
        F_rolling     — rolling resistance component (m × g × Crr)
        F_aero        — aerodynamic drag component (½ρCdAv²)
    """
    
    
    # The force needed to change the vehicle's speed
    # Only counts positive acceleration — braking doesn't require engine energy
    F_inertia = mass * max(a, 0.0)

    # Constant friction between tires and road surface
    F_rolling = mass * GRAVITY * Crr

    # Air resistance — grows with speed SQUARED
    # This is why aggressive high-speed driving burns so much more fuel
    F_aero = 0.5 * RHO_AIR * Cd * frontal_area * (v ** 2)

    # Total force — engine can only push forward, never negative
    F_traction = max(F_inertia + F_rolling + F_aero, 0.0)

    return F_traction, F_inertia, F_rolling, F_aero


def calculate_fuel_rate(F_traction, v, eta, fuel_LHV):
    """
    Equation 2 from Zacharof et al. (2024)
    Converts traction power to volumetric fuel consumption rate.

    FC_rate (L/s) = (F_traction × v) / (η × LHV × 3600)

    Parameters:
        F_traction  — traction force in Newtons (from Equation 1)
        v           — current speed in m/s
        eta         — powertrain efficiency factor (0 to 1)
        fuel_LHV    — lower heating value of fuel in Wh/L
                      (diesel = 9,950 Wh/L)

    Returns:
        fuel_rate_Ls — fuel consumption rate in Litres per second (L/s)

    Unit derivation (important to understand):
        Numerator:   F × v = [N × m/s] = [W] = [J/s]
        Denominator: η × LHV [Wh/L] × 3600 [s/h] = η × LHV [J/L]
        Result:      [J/s] ÷ [J/L] = [L/s]    ✓
    """
    P_traction = F_traction * v                    # power in Watts
    fuel_rate  = P_traction / (eta * fuel_LHV * 3600)
    return max(fuel_rate, 0.0)                     # never negative


def run_simulation(segments, behavior_name, behavior):
    """
    Runs the second-by-second fuel consumption simulation over a route.

    The vehicle drives through each segment one second at a time.
    At every timestep, Equations 1 and 2 are applied to compute
    the fuel consumed in that one second. All timestep fuels are
    accumulated into a total.

    No idle segments — vehicle maintains continuous motion throughout.
    Segment types handled: 'accelerate', 'cruise', 'decelerate', 'turn'

    Parameters
    ----------
    segments      : list of dicts — route segments from routes.py
                    Each dict has at minimum:
                        'type'     : str   — segment type
                        'distance' : float — segment length in metres
                    Decelerate segments also have:
                        'target_speed' : float — speed to slow down to [m/s]
                    All segments optionally have:
                        'label'    : str   — human-readable description

    behavior_name : str  — 'Aggressive', 'Moderate', or 'Eco'
    behavior      : dict — behavior profile from behavior.py
    vehicle       : dict — vehicle parameters from vehicle.py

    Returns
    -------
    log            : list of dicts — one entry per simulated second
    total_fuel_L   : float — total fuel consumed [litres]
    fuel_economy   : float — fuel economy [km/L]
    total_distance : float — total distance travelled [metres]
    """

    # ── STARTING CONDITIONS ───────────────────────────────────────────────────
    speed          = 0.0   # m/s  — vehicle starts from rest at Point A
    total_fuel_L   = 0.0   # L    — cumulative fuel consumed
    total_distance = 0.0   # m    — cumulative distance travelled
    log            = []    # list — one dict appended per timestep

    # ═════════════════════════════════════════════════════════════════════════
    # OUTER LOOP — work through each road segment in order
    # ═════════════════════════════════════════════════════════════════════════
    for seg in segments:

        seg_type = seg['type']
        seg_dist = seg['distance']
        label    = seg.get('label', seg_type)

        # ── DETERMINE THE TARGET SPEED FOR THIS SEGMENT ───────────────────────
        #
        # Each segment type has a goal speed the vehicle is moving toward:
        #
        #   accelerate → driver wants to reach cruise speed
        #   cruise     → driver holds cruise speed steady
        #   decelerate → driver wants to slow to a specific speed
        #                (could be 0 at final destination, or e.g. 5 m/s
        #                 for a slow roll through an intersection)
        #   turn       → driver navigates corner at corner_speed
        #
        if seg_type in ('accelerate', 'cruise'):
            target_v = behavior['cruise_speed']         # m/s

        elif seg_type == 'turn':
            target_v = behavior['corner_speed']         # m/s

        elif seg_type == 'decelerate':
            target_v = seg.get('target_speed', 0.0)     # m/s
            # NOTE: target_speed is defined per segment in routes.py
            # For turns: target_speed = corner entry speed (e.g. 5–8 m/s)
            # For final destination: target_speed = 0.0

        else:
            # Unknown segment type — skip with a warning
            print(f"  WARNING: Unknown segment type '{seg_type}' — skipping.")
            continue


        # INNER LOOP — step through this segment one second at a time
        dist_covered = 0.0
        safety_limit = int(seg_dist / 0.1) + 5000   # prevents infinite loops

        for _ in range(safety_limit):

            # EXIT CONDITION: segment fully travelled 
            if dist_covered >= seg_dist:
                break


            # Calculate the required acceleration this second
            #
            # speed_error = how far the current speed is from the target speed
            #   positive → vehicle needs to speed up
            #   negative → vehicle needs to slow down
            speed_error = target_v - speed

            if seg_type == 'cruise':
                # During cruising, use a gentle correction (40% of full rate)
                # so the vehicle doesn't oscillate around the target speed
                desired_a = (speed_error / DT) * 0.4
            else:
                # For all other phases, apply the full correction rate
                desired_a = speed_error / DT


            # Clip acceleration to behavior limits
            #
            # The behavior profile defines the physical limits of this driver:
            #   accel_rate : maximum forward acceleration (e.g. 2.0 m/s²)
            #   decel_rate : maximum braking (e.g. -2.8 m/s², negative)
            #
            # np.clip(value, min, max) keeps the value between min and max.
            # This is how driving behavior enters the physics calculation —
            # aggressive has a higher accel_rate, eco has a lower one.
            a = float(np.clip(
                desired_a,
                behavior['decel_rate'],   # minimum allowed (most negative)
                behavior['accel_rate']    # maximum allowed (most positive)
            ))


            # Update vehicle speed
            #
            # Basic kinematics: v(t) = v(t-1) + a × Δt
            # Clamped to 0 — vehicle cannot reverse
            speed = max(0.0, speed + a * DT)

            # Accumulate distance this second: d = v × t (t = 1s = DT)
            dist_step       = speed * DT
            dist_covered   += dist_step
            total_distance += dist_step


            # Check for coasting
            # Coasting occurs when:
            #   - The segment is a deceleration phase
            #   - The behavior allows coasting (eco and moderate do, aggressive doesn't)
            #   - The vehicle is actually decelerating (a < 0)
            #   - Speed is above a minimum threshold (not about to stop)
            #
            # When coasting, the driver has lifted off the throttle completely.
            # Modern diesel/petrol ECUs cut fuel injection during this condition.
            # Result: fuel consumption = 0 during the entire coasting period.
            #
            # This is one of the main reasons eco driving saves fuel —
            # it coasts early and often, accumulating many zero-fuel seconds.
            is_coasting = (
                seg_type == 'decelerate'
                and behavior['coast']      # True for eco and moderate
                and a < -0.05             # vehicle is genuinely slowing down
                and speed > 1.0           # above the minimum speed threshold
            )


            # EQUATION 1: Calculate traction force
            #
            # Three components:
            #   F_inertia = mass × acceleration (only positive a contributes)
            #   F_rolling = mass × g × Crr      (constant friction)
            #   F_aero    = ½ × ρ × Cd × A × v² (grows with speed squared)
            #
            # This is where driving behavior parameters directly feed in:
            #   → 'a' comes from the behavior's accel/decel rate (Step 2)
            #   → 'v' comes from the behavior's cruise speed (Steps 1–3)
            F_traction, F_inertia, F_rolling, F_aero = calculate_traction_force(
                v=speed,
                a=a,
                Cd=JEEPNEY_PARAMS["Cd"],
                mass=JEEPNEY_PARAMS["mass_empty"],
                frontal_area=JEEPNEY_PARAMS["frontal_area"],
                Crr=JEEPNEY_PARAMS["Crr"]
            )


            # EQUATION 2: Calculate fuel consumption rate
            #
            # If coasting → fuel rate = 0 (ECU fuel cut-off)
            # Otherwise   → FC (L/s) = (F × v) / (η × LHV × 3600)
            if is_coasting:
                FC_rate = 0.0
            else:
                FC_rate = calculate_fuel_rate(
                    F_traction=F_traction,
                    v=speed,
                    eta=ETA,
                    fuel_LHV=JEEPNEY_PARAMS["fuel_LHV"]
                )

            # Accumulate total fuel
            #
            # FC_rate is in L/s. Multiplying by DT (1 second) gives litres
            # consumed in this single timestep. Add to running total.
            total_fuel_L += FC_rate * DT

            # Log timestep for analysis and output

            log.append({
                'time':          len(log),
                'speed_kmh':     round(speed * 3.6, 2),
                'accel_ms2':     round(a, 3),
                'phase':         seg_type,
                'segment_label': label,
                'coasting':      is_coasting,
                'F_inertia_N':   round(F_inertia, 1),
                'F_rolling_N':   round(F_rolling, 1),
                'F_aero_N':      round(F_aero, 1),
                'F_traction_N':  round(F_traction, 1),
                'P_traction_W':  round(F_traction * speed, 1),
                'FC_rate_mLs':   round(FC_rate * 1000, 5),
                'total_fuel_L':  round(total_fuel_L, 6),
                'distance_m':    round(total_distance, 1),
                'behavior':      behavior_name,
            })

            # EXIT CONDITION: vehicle has reached a full stop
            # Only relevant for the final decelerate segment (target_v = 0)
            if target_v <= 0 and speed <= 0:
                break

    # compute final summary metrics
    distance_km  = total_distance / 1000.0
    fuel_economy = (distance_km / total_fuel_L) if total_fuel_L > 1e-9 else 0.0

    return log, total_fuel_L, fuel_economy, total_distance



#print(run_simulation(segments=ROUTES["route_1"]["segments"], behavior_name="eco", behavior=BEHAVIOR_PROFILES["Eco"]))


log, total_fuel, fuel_economy, total_distance = run_simulation(
    segments=ROUTES["route_1"]["segments"],
    behavior_name="Eco",
    behavior=BEHAVIOR_PROFILES["Eco"]
)

print("\n" + "="*100)
print("JEEPNEY FUEL CONSUMPTION SIMULATION")
print("="*100)

print(f"Total Distance : {total_distance/1000:.2f} km")
print(f"Total Fuel     : {total_fuel:.4f} L")
print(f"Fuel Economy   : {fuel_economy:.2f} km/L")

df = pd.DataFrame(log)
print(df[[
    "time",
    "phase",
    "speed_kmh",
    "accel_ms2",
    "FC_rate_mLs",
    "total_fuel_L",
    "distance_m",
    "coasting"
]].to_string(index=False))

print("="*100)

