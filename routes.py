ROUTES = {
    "route_1": {
        "name": "sucat to baclaran",
        "distance_km": 6.24,

        "segments": [
            {'type': 'accelerate',  'distance': 400,  'label': 'Sucat terminal departure - Dr. A. Santos Ave / SLEx service road'},
            {'type': 'cruise',      'distance': 1000, 'label': 'Dr. A. Santos Ave - commercial stretch'},
            {'type': 'decelerate',  'distance': 60,   'target_speed': 0,  'label': 'Passenger stop - SM City Sucat area'},
            {'type': 'idle',        'distance': 0,    'duration': 22,     'label': 'Passenger boarding - SM City Sucat'},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after SM Sucat stop'},
            {'type': 'cruise',      'distance': 2000, 'label': 'Dr. A. Santos Ave - mid route with signalized intersections'},
            {'type': 'decelerate',  'distance': 80,   'target_speed': 0,  'label': 'Intersection stop - Presidents Ave'},
            {'type': 'idle',        'distance': 0,    'duration': 20,     'label': 'Signal wait - Presidents Ave'},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after Presidents Ave'},
            {'type': 'decelerate',  'distance': 100,  'target_speed': 8.3, 'label': 'Dr. A. Santos Ave to Ninoy Aquino Ave junction'},
            {'type': 'turn',        'distance': 60,   'label': 'Turn onto Ninoy Aquino Ave'},
            {'type': 'cruise',      'distance': 2000, 'label': 'Ninoy Aquino Ave - NAIA-adjacent heavy traffic'},
            {'type': 'decelerate',  'distance': 60,   'target_speed': 0,  'label': 'Passenger stop 1 - Ninoy Aquino Ave'},
            {'type': 'idle',        'distance': 0,    'duration': 22,     'label': 'Passenger boarding - Ninoy Aquino Ave stop 1'},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after Ninoy Aquino stop 1'},
            {'type': 'decelerate',  'distance': 60,   'target_speed': 0,  'label': 'Passenger stop 2 - Ninoy Aquino Ave'},
            {'type': 'idle',        'distance': 0,    'duration': 22,     'label': 'Passenger boarding - Ninoy Aquino Ave stop 2'},
            {'type': 'accelerate',  'distance': 80,   'label': 'Re-accelerate after Ninoy Aquino stop 2'},
            {'type': 'decelerate',  'distance': 100,  'target_speed': 0,  'label': 'Approach Baclaran terminal - Roxas Blvd area'},
        ]
    }
}