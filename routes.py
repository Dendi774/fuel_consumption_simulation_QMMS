ROUTES = {
    "route_1": {
        "name": "baclaran to tambo",
        "distance_km": 1.84,
         
         "segments": [
            {'type': 'accelerate',  'distance': 200,  'label': 'Entering Roxas Blvd'},
            {'type': 'cruise',      'distance': 1400,  'label': 'Roxas Blvd straight'},
            {'type': 'decelerate',  'distance': 80,   'target_speed': 8.3,
                                                       'label': 'Tambo turn approach'},
            {'type': 'turn',        'distance': 60,   'label': 'Into Tambo'},
            {'type': 'decelerate',  'distance': 100,  'target_speed': 0,
                                                       'label': 'Approaching terminal'},
         ]
    }
}