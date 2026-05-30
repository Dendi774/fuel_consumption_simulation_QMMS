BEHAVIOR_PROFILES = {
    'Aggressive': {
        'label': 'Aggressive',
        'color': 'red',
        'accel_rate': 2.5,       # m/s² — how fast it speeds up
        'decel_rate': -3.0,      # m/s² — how fast it slows down
        'cruise_speed': 70/3.6,  # m/s — convert km/h to m/s (60 km/h)
        'corner_speed': 25/3.6,  # m/s — speed through turns
        'coast': False,          # does not coast during deceleration
    },

    'Moderate': {
        'label': 'Moderate',
        'color': 'orange',
        'accel_rate': 0.9,
        'decel_rate': -1.5,
        'cruise_speed': 50/3.6,
        'corner_speed': 20/3.6,
        'coast': True,
    },

    'Eco': {
        'label': 'Eco',
        'color': 'green',
        'accel_rate': 0.45,
        'decel_rate': -0.75,
        'cruise_speed': 40/3.6,
        'corner_speed': 15/3.6,
        'coast': True,
    },
}