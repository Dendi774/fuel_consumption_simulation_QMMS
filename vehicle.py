JEEPNEY_PARAMS = {
    'name': 'Modern Philippine Jeepney (Isuzu 4JB1)',
    'mass_empty': 2750,         # kg — curb weight, no passengers
    'mass_loaded': None,        # kg — variable
    'Cd': 0.625,                 # drag coefficient — boxy shape
    'frontal_area': 3.25,        # m² — calculated from dimensions
    'Crr': 0.015,               # rolling resistance
    'fuel_LHV': 9950, # not final           # Wh/L — diesel lower heating value
    'fuel_density': 0.832,      # kg/L — diesel density
    'eta_mt': 0.84,             # drivetrain efficiency, manual diesel
    'co2_per_litre': 2640 # Not final,      # g CO2 per litre of diesel burned
}