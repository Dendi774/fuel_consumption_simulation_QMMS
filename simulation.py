# Jeepney Fuel Consumption Simulation Engine
#
# Physics model:
#   Zacharof, N. et al. (2024). "A simulation model of the real-world fuel
#   and energy consumption of light-duty vehicles."
#   Frontiers in Future Transportation, Vol. 5.
#   https://doi.org/10.3389/ffutr.2024.1334651
#
# Equation 1 — Traction Force:
#   F = (m × a) + (m × g × Crr) + (½ × ρ × Cd × A × v²)
#
# Equation 2 — Fuel Flow Rate:
#   FC (L/s) = (F × v) / (η × LHV × 3600)

import numpy as np
import pandas as pd

from vehicle   import JEEPNEY_PARAMS
from behaviors import BEHAVIOR_PROFILES
from routes    import ROUTES


# PHYSICAL CONSTANTS
RHO_AIR = 1.225   # kg/m³ — standard sea-level air density (ISO 2533)
GRAVITY = 9.81    # m/s²  — gravitational acceleration
DT      = 1.0     # s     — simulation timestep (1 second)


# COMBINED POWERTRAIN EFFICIENCY  η
#
# η = engine thermal efficiency × drivetrain mechanical efficiency
#   = 0.35  ×  eta_mt
#
# Engine thermal efficiency 0.35:
#   Source: Heywood, J.B. (1988). Internal Combustion Engine Fundamentals.
#           McGraw-Hill. / National Academies Press (2010).
#
# Drivetrain mechanical efficiency (eta_mt from vehicle.py):
#   Source: Gillespie, T.D. (1992). Fundamentals of Vehicle Dynamics.
#           SAE International. / Zacharof et al. (2024).
#
# η is constant throughout the simulation. This is valid because the
# objective is to compare RELATIVE fuel consumption across behaviors.
# Since η applies equally to all three behaviors, it does not affect
# the relative comparison — only the absolute fuel quantities.

ETA = JEEPNEY_PARAMS["eta_mt"] * 0.35


# IDLE FUEL CONSUMPTION RATE  (fixed constant — bypasses Equation 2)
#
# At v = 0: Equation 2 gives FC = (F × 0) / (...) = 0  — which is wrong.
# The engine at idle burns fuel to overcome internal friction at low RPM.
# This requires a separately sourced measured rate.
#
# Value derivation:
#   2.0L diesel idle rate = 0.17 gal/hr = 0.643 L/hr  (US DOE Fact #861, 2015)
#   Scaled to 2.8L Isuzu 4JB1: 0.643 × (2.8 / 2.0)  = 0.900 L/hr
#   Converted to L/s:           0.900 / 3600           = 0.000250 L/s
#
# Sources:
#   US DOE Fact #861 — Argonne National Laboratory (2015)
#   https://www.energy.gov/cmei/vehicles/fact-861-february-23-2015-...
#
#   Shancita et al. (2013). Impact of idling on fuel consumption and exhaust
#   emissions. ScienceDirect. doi:10.1016/j.enconman.2013.03.028

IDLE_FUEL_RATE_LS = 0.900 / 3600   # L/s = 0.000250 L/s = 0.25 mL/s


# EQUATION 1 — TRACTION FORCE
def calculate_traction_force(v, a):
    """
    Equation 1 from Zacharof et al. (2024).

    F_traction = (m × a) + (m × g × Crr) + (½ × ρ × Cd × A × v²)

    The three components represent three separate resistive forces
    the engine must overcome to maintain or change the vehicle's speed:

      F_inertia — force required to change speed (Newton's 2nd Law)
                  Only positive acceleration contributes — braking
                  is handled by brakes, not the engine.

      F_rolling — constant friction between tires and road surface.
                  Always present while vehicle is moving.

      F_aero    — aerodynamic drag from air resistance.
                  Grows with speed SQUARED — the main reason high-speed
                  driving is so much less fuel-efficient.

    Grade force (m × g × sinθ) is omitted — flat road scope (θ = 0°).

    Parameters
        v : float — current speed in m/s
        a : float — current acceleration in m/s² (+ = speeding up)

    Returns
        F_traction : float — total traction force in Newtons [N]
        F_inertia  : float — inertial component [N]
        F_rolling  : float — rolling resistance component [N]
        F_aero     : float — aerodynamic drag component [N]
    """
    F_inertia  = JEEPNEY_PARAMS["mass_empty"] * max(a, 0.0)
    F_rolling  = JEEPNEY_PARAMS["mass_empty"] * GRAVITY * JEEPNEY_PARAMS["Crr"]
    F_aero     = (0.5 * RHO_AIR
                  * JEEPNEY_PARAMS["Cd"]
                  * JEEPNEY_PARAMS["frontal_area"]
                  * (v ** 2))
    F_traction = max(F_inertia + F_rolling + F_aero, 0.0)

    return F_traction, F_inertia, F_rolling, F_aero


# EQUATION 2 — FUEL FLOW RATE
def calculate_fuel_rate(F_traction, v):
    """
    Equation 2 from Zacharof et al. (2024).

    FC_rate (L/s) = (F_traction × v) / (η × LHV_fuel × 3600)

    Converts the traction power the engine produces into a volumetric
    fuel consumption rate using the combined powertrain efficiency η
    and the lower heating value of diesel fuel.

    Unit derivation:
        Numerator:   F [N] × v [m/s]          = P [W]   = P [J/s]
        Denominator: η × LHV [Wh/L] × 3600    = η × LHV [J/L]
        Result:      [J/s] ÷ [J/L]            = [L/s]   ✓

    Parameters
        F_traction : float — traction force from Equation 1 [N]
        v          : float — current speed [m/s]

    Returns
        float — fuel consumption rate [L/s]
    """
    P_traction = F_traction * v
    fuel_rate  = P_traction / (ETA * JEEPNEY_PARAMS["fuel_LHV"] * 3600)
    return max(fuel_rate, 0.0)



# MAIN SIMULATION FUNCTION
def run_simulation(segments, behavior_name, behavior):
    """
    Runs the second-by-second fuel consumption simulation over a route.

    Algorithm:
        FOR each segment in the route:

            IF idle segment:
                REPEAT for seg['duration'] seconds:
                    FC = IDLE_FUEL_RATE_LS  (fixed constant, not Equation 2)
                    total_fuel += FC × 1s
                    log one row
                SKIP to next segment

            ELSE (accelerate / cruise / decelerate / turn):
                Determine target speed for this segment type
                REPEAT until dist_covered >= seg_dist:
                    Step 1: Calculate desired acceleration
                    Step 2: Clip to behavior limits  [behavior enters here]
                    Step 3: Update speed  v = v + a × 1s
                    Step 4: Accumulate distance (clamped to segment boundary)
                    Step 5: Check for coasting  [behavior enters here]
                    Step 6: Equation 1 → F_traction  [behavior enters here via a and v]
                    Step 7: Equation 2 → FC_rate  (or 0 if coasting)
                    Step 8: total_fuel += FC_rate × 1s
                    Step 9: Log one row

        Fuel economy = route_distance_km / total_fuel_L

    Parameters
        segments      : list of segment dicts from routes.py
        behavior_name : str  — 'Aggressive', 'Moderate', or 'Eco'
        behavior      : dict — behavior profile from behaviors.py

    Returns
        log              : list of dicts — one entry per simulated second
        total_fuel_L     : float — total fuel consumed [L]
        fuel_economy     : float — fuel economy [km/L]
        route_distance_km: float — declared route distance [km]
    """

    # Starting state
    speed          = 0.0   # m/s — vehicle starts from rest at Point A
    total_fuel_L   = 0.0   # L   — cumulative fuel consumed
    total_distance = 0.0   # m   — cumulative simulated distance
    log            = []    # list — one dict appended every simulated second

    # OUTER LOOP — process each road segment in order
    for seg in segments:

        seg_type = seg['type']
        seg_dist = seg['distance']
        label    = seg.get('label', seg_type)

        # IDLE SEGMENT
        # Vehicle is stopped, engine is running.
        # Equation 2 cannot be used (v=0 gives zero fuel — wrong).
        # Fixed idle fuel rate from published DOE/ANL measured data instead.
        # Duration comes from the segment definition in routes.py.
        if seg_type == 'idle':

            idle_duration = int(seg.get('duration', 20))

            for _ in range(idle_duration):

                # Fixed idle rate — not from Equation 2
                FC_idle       = IDLE_FUEL_RATE_LS
                total_fuel_L += FC_idle * DT

                log.append({
                    'time':          len(log),
                    'speed_kmh':     speed * 3.6,
                    'accel_ms2':     0.0,
                    'phase':         'idle',
                    'segment_label': label,
                    'coasting':      False,
                    'F_inertia_N':   0.0,
                    'F_rolling_N':   0.0,
                    'F_aero_N':      0.0,
                    'F_traction_N':  0.0,
                    'P_traction_W':  0.0,
                    'FC_rate_mLs':   round(FC_idle * 1000, 5),
                    'total_fuel_L':  round(total_fuel_L, 6),
                    'distance_m':    round(total_distance, 1),
                    'behavior':      behavior_name,
                })

            # Skip the driving logic below — go to next segment
            continue

        # DETERMINE TARGET SPEED
        #
        # Every driving segment has a speed it is working toward.
        # The vehicle moves toward this speed over multiple timesteps.
        #
        #   accelerate / cruise  →  behavior's cruise speed
        #   turn                 →  behavior's corner speed
        #   decelerate           →  segment's declared target speed
        #                           (0 = full stop, e.g. 8.3 = slow turn entry)
        if seg_type in ('accelerate', 'cruise'):
            target_v = behavior['cruise_speed']
        elif seg_type == 'turn':
            target_v = behavior['corner_speed']
        elif seg_type == 'decelerate':
            target_v = seg.get('target_speed', 0.0)
        else:
            print(f"  WARNING: Unknown segment type '{seg_type}' — skipping.")
            continue

        # INNER LOOP — step through this segment one second at a time
        dist_covered = 0.0

        while dist_covered < seg_dist:
            # STEP 1: Calculate desired acceleration 
            #
            # speed_error = how far we are from the target speed
            #   positive → need to speed up
            #   negative → need to slow down
            #
            # cruise uses a dampened correction (× 0.4) to prevent the speed
            # from oscillating above and below the target each second.
            speed_error = target_v - speed

            if seg_type == 'decelerate':
                
                remaining = max(seg_dist - dist_covered, 0.1)
                desired_a = (
                    (target_v**2 - speed**2)
                    / (2 * remaining)
                )
                
            else:
                desired_a = speed_error / DT

            # STEP 2: Clip to behavior's physical limits
            #
            # This is one of three places behavior directly enters the physics.
            # The behavior profile defines the driver's maximum acceleration
            # and maximum braking rate. np.clip enforces those limits.
            #
            # Aggressive: accel_rate = 2.0,  decel_rate = -2.8
            # Eco:        accel_rate = 0.45, decel_rate = -0.75
            a = float(np.clip(
                desired_a,
                behavior['decel_rate'],   # minimum (most negative)
                behavior['accel_rate']    # maximum (most positive)
            ))

            # STEP 3: Update vehicle speed
            #
            # Basic kinematics: v(t) = v(t-1) + a × Δt
            # max(0.0, ...) prevents the vehicle from going backwards
            speed = max(0.0, speed + a * DT)

            # STEP 4: Accumulate distance
            #
            # d = v × t  (t = 1 second)
            # Clamped to the remaining segment distance to prevent overshoot.
            # Without clamping, a fast vehicle would add too much distance
            # in the last step of each segment.
            dist_step = speed * DT
            remaining = seg_dist - dist_covered
            dist_step = min(dist_step, remaining)   # clamp to boundary

            dist_covered   += dist_step
            total_distance += dist_step

            # STEP 5: Check for coasting
            #
            # Coasting = driver lifts off throttle during deceleration.
            # Modern diesel ECUs cut fuel injection during coasting.
            # Result: FC_rate = 0 for the entire coasting period.
            #
            # This is the second place behavior enters:
            #   Eco and Moderate: coast = True  → zero fuel during decel
            #   Aggressive:       coast = False → fuel burns during decel
            is_coasting = (
                seg_type == 'decelerate'
                and behavior['coast']    # True for eco and moderate only
                and a < -0.05           # actually decelerating
                and speed > 1.0         # above minimum speed threshold
            )

            # STEP 6: Equation 1 — Traction Force
            #
            # This is the third place behavior enters:
            #   → 'a' in F_inertia comes from Step 2 (behavior's accel limit)
            #   → 'v' in F_aero comes from Step 3 (behavior's cruise speed)
            #
            # If coasting, skip — no traction force needed (engine not engaged)
            if is_coasting:
                F_traction = 0.0
                F_inertia  = 0.0
                F_rolling  = JEEPNEY_PARAMS["mass_empty"] * GRAVITY * JEEPNEY_PARAMS["Crr"]
                F_aero     = (0.5 * RHO_AIR * JEEPNEY_PARAMS["Cd"]
                              * JEEPNEY_PARAMS["frontal_area"] * (speed ** 2))
            else:
                F_traction, F_inertia, F_rolling, F_aero = calculate_traction_force(
                    v=speed,
                    a=a
                )

            # STEP 7: Equation 2 — Fuel Rate
            #
            # If coasting → FC_rate = 0  (ECU fuel cut-off)
            # Otherwise   → FC_rate = (F × v) / (η × LHV × 3600)
            if is_coasting:
                FC_rate = 0.0
            else:
                FC_rate = calculate_fuel_rate(F_traction=F_traction, v=speed)

            # STEP 8: Accumulate total fuel
            #
            # FC_rate is in L/s. Multiplying by 1 second gives litres
            # burned in this single timestep. Added to running total.
            total_fuel_L += FC_rate * DT

            # STEP 9: Log this timestep
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



    # POST-LOOP: COMPUTE FINAL METRICS
    # Use declared route distance (sum of all segment distances) as the
    # denominator for fuel economy. This ensures all three behaviors are
    # compared against the same road length, making km/L directly comparable.
    route_distance_m  = sum(seg['distance'] for seg in segments)
    route_distance_km = route_distance_m / 1000.0

    fuel_economy = (route_distance_km / total_fuel_L) if total_fuel_L > 1e-9 else 0.0

    return log, total_fuel_L, fuel_economy, route_distance_km



# DISPLAY FUNCTIONS
def print_summary(behavior_name, total_fuel_L, fuel_economy,
                  route_distance_km, log):
    """Prints the summary result for one behavior on one route."""

    EMOJI = {'Aggressive': '🔴', 'Moderate': '🟡', 'Eco': '🟢'}
    df    = pd.DataFrame(log)

    print(f"\n{'='*65}")
    print(f"  {EMOJI.get(behavior_name,'•')}  {behavior_name.upper()}")
    print(f"{'='*65}")
    print(f"  Distance        : {route_distance_km:.3f} km")
    print(f"  Duration        : {len(log)} seconds")
    print(f"  Total fuel      : {total_fuel_L*1000:.2f} mL  ({total_fuel_L:.5f} L)")
    print(f"  Fuel economy    : {fuel_economy:.2f} km/L  ({100/fuel_economy:.1f} L/100km)")
    print(f"  Average speed   : {df['speed_kmh'].mean():.1f} km/h")
    print(f"  Max speed       : {df['speed_kmh'].max():.1f} km/h")
    print(f"  Coasting time   : {df['coasting'].mean()*100:.1f}% of journey")

    # Fuel by phase
    print(f"\n  Fuel by driving phase:")
    print(f"  {'Phase':>12}  {'Seconds':>8}  {'Avg mL/s':>9}  "
          f"{'Fuel mL':>9}  {'% of total':>10}")
    print(f"  {'─'*12}  {'─'*8}  {'─'*9}  {'─'*9}  {'─'*10}")

    for phase in ['accelerate', 'cruise', 'decelerate', 'turn', 'idle']:
        sub = df[df['phase'] == phase]
        if sub.empty:
            continue
        secs      = len(sub)
        avg_fc    = sub['FC_rate_mLs'].mean()
        fuel_phase= sub['FC_rate_mLs'].sum() * DT
        pct       = fuel_phase / (total_fuel_L * 1000) * 100

        print(f"  {phase:>12}  {secs:>8}  {avg_fc:>9.5f}  "
              f"{fuel_phase:>9.3f}  {pct:>9.1f}%")


def print_comparison(route_name, results):
    """Prints the side-by-side comparison for all behaviors on one route."""

    print(f"\n\n{'#'*65}")
    print(f"  COMPARISON — {route_name}")
    print(f"{'#'*65}")
    print(f"  {'':2}  {'Behavior':>12}  {'Fuel (mL)':>10}  "
          f"{'km/L':>7}  {'L/100km':>8} ")
    print(f"  {'─'*2}  {'─'*12}  {'─'*10}  "
          f"{'─'*7}  {'─'*8} ")

    EMOJI = {'Aggressive': '🔴', 'Moderate': '🟡', 'Eco': '🟢'}

    for bname in ['Aggressive', 'Moderate', 'Eco']:
        if bname not in results:
            continue
        r   = results[bname]
        print(f"  {EMOJI[bname]}  {bname:>12}  "
              f"{r['fuel']*1000:>10.2f}  "
              f"{r['economy']:>7.2f}  "
              f"{100/r['economy']:>8.2f}  ")

    # Savings vs aggressive
    if 'Aggressive' in results:
        base = results['Aggressive']['fuel']
        print()
        for bname in ['Moderate', 'Eco']:
            if bname not in results:
                continue
            saved    = base - results[bname]['fuel']
            pct      = saved / base * 100
            print(f"  {EMOJI[bname]}  {bname} saves  "
                  f"{saved*1000:.2f} mL  ({pct:.1f}% less fuel)  |  ")


# ENTRY POINT
if __name__ == '__main__':
    print('=' * 65)
    print('  PARANAQUE JEEPNEY FUEL CONSUMPTION SIMULATION')
    print('  Physics model : Zacharof et al. (2024)')
    print('  Vehicle       : ' + JEEPNEY_PARAMS['name'])
    print(f'  η (ETA)       : {ETA:.4f}  '
          f'(eta_mt {JEEPNEY_PARAMS["eta_mt"]} × thermal 0.35)')
    print('  Grade         : 0  (flat road — all routes)')
    print('=' * 65)

    # Run every route × every behavior
    for route_id, route_data in ROUTES.items():

        route_name = route_data['name']
        segments   = route_data['segments']

        print(f'\n\n{"#"*65}')
        print(f'  ROUTE : {route_name}')
        print(f'{"#"*65}')

        route_results = {}

        for bname, bprofile in BEHAVIOR_PROFILES.items():

            log, total_fuel_L, fuel_economy, route_distance_km = run_simulation(
                segments      = segments,
                behavior_name = bname,
                behavior      = bprofile,
            )

            route_results[bname] = {
                'log':      log,
                'fuel':     total_fuel_L,
                'economy':  fuel_economy,
                'distance': route_distance_km,
            }

            print_summary(bname, total_fuel_L, fuel_economy,
                          route_distance_km, log)

        print_comparison(route_name, route_results)

    print(f'\n\n{"="*65}')
    print('  SIMULATION COMPLETE')
    print(f'  η = {ETA:.4f}  (constant across all behaviors and phases)')
    print('  Idle fuel rate = 0.25 mL/s  (DOE/ANL measured data)')
    print('  Coasting → FC = 0  (ECU fuel cut-off, Eco and Moderate)')
    print('  Fuel economy uses declared route distance (consistent denominator)')
    print(f'{"="*65}')